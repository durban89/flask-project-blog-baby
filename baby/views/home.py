#! _*_ coding: utf-8 _*_

import os
from flask import Blueprint, render_template, send_from_directory, current_app

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/')
def index():
    return render_template('home/index.j2')


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')
