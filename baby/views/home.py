#! _*_ coding: utf-8 _*_

import os

from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    current_app,
    make_response,
    request,
    escape
)
from baby.helper.captcha import Captcha

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/')
def index():
    return render_template('home/index.j2')


@bp.route('/captcha')
def captcha():
    font_path = os.path.join(current_app.root_path, 'static/fonts/Vera.ttf')
    captcha = Captcha(font_path, 2)

    out = StringIO()
    image = captcha.captcha()
    image.save(out, "PNG")
    out.seek(0)

    response = make_response(out.read())
    response.content_type = 'image/png'
    return response


@bp.route('/captcha/validate')
def captcha_validate():
    code = request.args.get('code')
    if Captcha.captcha_validate(escape(code)):
        return 'captcha validate correct'
    else:
        return 'captcha validate failed'


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')
