#! _*_ coding: utf-8 _*_
import functools
import logging
import time
import re
from os import urandom
from datetime import timedelta
from base64 import urlsafe_b64encode

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app
)

from werkzeug.security import check_password_hash, generate_password_hash
from baby.db import get_db
from baby.helper.captcha import Captcha
from baby.celery import create_celery

bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_http_domain():
    url_scheme = request.environ.get('wsgi.url_scheme')
    host = request.environ.get('HTTP_HOST')

    return '%s://%s' % (url_scheme, host)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        code = request.form['verification-code']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif username and registered_username(username):
            error = 'Username has been registered.'
        elif username and not check_username_safe(username):
            error = 'Username is invalidate.'
        elif not password:
            error = 'Password is required.'
        elif password and not check_password_safe(password):
            error = 'Password is not safety.'
        elif not email:
            error = 'Email is required.'
        elif email and registered_email(email):
            error = 'Email has been registered.'
        elif email and not check_email_safe(email):
            error = 'Email address is invalidate.'
        elif not code:
            error = 'Verification code is required'
        elif code and not Captcha.captcha_validate(code):
            error = 'Verification code is wrong'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'user {} is already registered.'.format(username)

        ctime = int(time.time())
        if error is None:
            db.execute(
                'INSERT INTO user (username, email, password, ctime) '
                'VALUES (?, ?, ?, ?)',
                (username, email, generate_password_hash(password), ctime)
            )
            db.commit()

            send_register_email(get_http_domain(), username, email)

            return render_template(
                'auth/register_success.j2',
                email=email
            )
            # return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.j2')


def check_username_safe(username):
    length_error = len(username) < 3

    username_error = re.search(r'[a-zA-Z]', username) is None

    return not (length_error or username_error)


def check_email_safe(email):
    email_error = re.search(
        r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email) is None

    return not email_error


def check_password_safe(password):
    # 长度 至少8位
    length_error = len(password) < 8

    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(
        r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None

    ok = not (
        length_error or
        digit_error or
        uppercase_error or
        lowercase_error or
        symbol_error
    )

    return ok


def registered_username(username):
    db = get_db()
    row = db.execute(
        'SELECT * FROM user WHERE username = ? and username <> ""',
        (username,)
    ).fetchone()

    if row is None:
        return False
    else:
        return True


def registered_email(email):
    db = get_db()
    row = db.execute(
        'SELECT * FROM user WHERE email = ? and email <> ""',
        (email,)
    ).fetchone()

    if row is None:
        return False
    else:
        return True


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        code = request.form['verification-code']

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user '
            ' WHERE (username = ? OR email = ?)'
            ' AND email <> "" and status = 1',
            (username, username)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
            current_app.logger.error(
                '%s logged fail - username is wrong', username)
        elif not check_password_hash(user['password'], password):
            current_app.logger.error(
                '%s logged fail - password is wrong', username)
            error = 'Incorrect password.'
        elif not code:
            error = 'Verification code is required'
        elif code and not Captcha.captcha_validate(code):
            error = 'Verification code is wrong'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            current_app.logger.info('%s logged successfully', username)

            celery = create_celery(current_app)
            celery.send_task(
                name='tasks.send_login_email',
                args=[
                    get_http_domain(),
                    user['username'],
                    user['email']
                ]
            )
            current_app.logger.info('%s logged successfully other ', username)

            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.j2')


@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('blog.index'))


@bp.route('/find/password/activate', methods=['GET', 'POST'])
def find_password_activate():
    '''找回密码激活'''
    if request.method == 'POST':
        password = request.form['password']
        code = request.args.get('code')

        db = get_db()

        row = db.execute(
            'SELECT * FROM find_password_verify WHERE code = ?',
            (code,)
        ).fetchone()

        if row is None:
            flash('验证失败')
        else:
            row = dict(row)
            ctime = int(time.time())
            if ctime > row['expired']:
                flash('链接已过期，请重新提交')
            else:
                db.execute(
                    'UPDATE user SET password=? WHERE email = ?',
                    (generate_password_hash(password), row['email'])
                )
                db.execute(
                    'UPDATE find_password_verify SET expired = 0 WHERE id = ?',
                    (row['id'],)
                )
                db.commit()

                flash('密码设置成功', 'success')

    return render_template('auth/find_password_activate.j2')


def check_find_password_email_is_expired(row, ctime):
    '''检查发送重置密码的邮件是否过期'''
    row = dict(row)

    if row and row['expired'] > ctime:
        return False

    return True


@bp.route('/find/password', methods=['GET', 'POST'])
def find_password():
    if request.method == 'POST':
        email = request.form['email']
        if email is None:
            flash('Email address is empty', 'warning')
        elif email and not check_email_safe(email):
            flash('Email address is invalidate', 'warning')
        else:
            db = get_db()
            row = db.execute(
                'SELECT * FROM user WHERE email = ?',
                (email,)
            ).fetchone()

            if row is None:
                flash('Email is not registered', 'warning')
            else:
                row = db.execute(
                    'SELECT * FROM find_password_verify WHERE email = ?'
                    ' ORDER BY id DESC',
                    (email,)
                ).fetchone()

                ctime = int(time.time())

                if row and \
                        not check_find_password_email_is_expired(row, ctime):
                    flash('so quickly, please slowly', 'warning')
                else:
                    code = urlsafe_b64encode(urandom(64)).decode('utf-8')

                    # 过期时间30分钟
                    delta = timedelta(minutes=30)

                    expired = ctime + delta.seconds

                    db.execute(
                        'INSERT INTO find_password_verify'
                        ' (email, code, expired, ctime) VALUES (?,?,?,?)',
                        (email, code, expired, ctime)
                    )
                    db.commit()

                    celery = create_celery(current_app)
                    celery.send_task(
                        name='tasks.find_pass_email',
                        args=[
                            get_http_domain(),
                            email,
                            code
                        ])
                    flash('Email send success', 'info')

    return render_template('auth/find_password.j2')


@bp.route('/register/activate')
def register_activate():
    code = request.args.get('code')

    db = get_db()
    row = db.execute(
        'SELECT * FROM user_email_verify WHERE code=?',
        (code,)
    ).fetchone()

    if row is None:
        return render_template(
            'auth/email_verify_erorr.j2',
            msg='验证失败'
        )
    else:
        row = dict(row)
        ctime = int(time.time())
        if ctime > row['expired']:
            return render_template(
                'auth/email_verify_erorr.j2',
                msg='验证链接已过期'
            )

        db.execute(
            'UPDATE user SET status=1 WHERE email=?',
            (row['email'],)
        )
        db.execute(
            'UPDATE user_email_verify SET expired=0 WHERE id=?',
            (row['id'],)
        )
        db.commit()

        return redirect(url_for('auth.login'))


def send_register_email(domain, username, email):
    db = get_db()
    code = urlsafe_b64encode(urandom(64)).decode('utf-8')

    # 过期时间30分钟
    delta = timedelta(minutes=30)
    ctime = int(time.time())
    expired = ctime + delta.seconds

    db.execute(
        'INSERT INTO user_email_verify'
        ' (email, code, expired, ctime) VALUES (?,?,?,?)',
        (email, code, expired, ctime)
    )
    db.commit()

    celery = create_celery(current_app)
    celery.send_task(name='tasks.send_register_email',
                     args=[
                         domain,
                         username,
                         email,
                         code
                     ])

    return 'test'


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
