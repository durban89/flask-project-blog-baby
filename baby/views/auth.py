#! _*_ coding: utf-8 _*_
import functools
import logging

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

bp = Blueprint('auth', __name__, url_prefix='/auth')


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
        code = request.form['verification-code']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not code:
            error = 'Verification code is required'
        elif code and not Captcha.captcha_validate(code):
            error = 'Verification code is wrong'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'user {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.j2')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        code = request.form['verification-code']

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
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
            logging.info('%s logged successfully', username)
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.j2')


@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('blog.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
