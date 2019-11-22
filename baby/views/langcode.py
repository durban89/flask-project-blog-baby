# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-11 12:00:49
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-21 14:54:02

from flask import (
    Blueprint,
    g,
    request,
    render_template,
    flash,
    url_for,
    redirect
)
from baby.extensions import cache
from baby.decorator import templated, cached
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from baby.model import Movie, Imdb

bp = Blueprint('langcode', __name__, url_prefix='/<lang_code>/langcode')


class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=4, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=4, max=25),
        validators.EqualTo('confirm', message='Password not match')])
    confirm = PasswordField(
        'Repeat Password', [validators.Length(min=4, max=25)])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


@bp.url_defaults
def add_language_code(endpoint, values):
    values.setdefault(
        'lang_code', g.lang_code if 'lang_code' in g else 'zh')


@bp.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@bp.route('/')
def index():
    print(request.endpoint)
    return 'langcode'


@bp.route('/template', methods=['GET'])
@templated('langcode/template.j2')
def template():
    return {
        'values': 24
    }


@bp.route('/about', methods=['GET'])
@cache.cached(timeout=50)
def about():
    print('call about func')
    return g.lang_code + ' 介绍'


@bp.route('/contact', methods=['GET'])
@cached()
def contact():
    print('call contact func')
    return g.lang_code + ' Contact'


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        print(form.username.data)
        print(form.password.data)
        print(form.email.data)

        flash('Thanks for register')
        # return redirect(url_for('langcode.login'))
        return redirect(request.url)
    return render_template('langcode/register.j2', form=form)


def create_me():
    bttf = Movie(title='Back To The Feature', year=1985)
    bttf.actors = [
        'Michael J. Fox',
        'Christopher Lloyd'
    ]
    bttf.imdb = Imdb(imdb_id='tt0088763', rating=8.5)
    bttf.save()

    return redirect(url_for('langcode.me'))


def me():
    movies = Movie.objects(title='Back To The Feature')

    return render_template('langcode/me.j2', movies=movies)
