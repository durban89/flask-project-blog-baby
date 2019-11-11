# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-11 12:00:49
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-11 16:40:13

from flask import (
    Blueprint,
    g
)
from baby.extensions import cache


bp = Blueprint('langcode', __name__, url_prefix='/<lang_code>/langcode')


@bp.url_defaults
def add_language_code(endpoint, values):
    values.setdefault(
        'lang_code', g.lang_code if 'lang_code' in g else 'zh')


@bp.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@bp.route('/')
def index():
    return 'langcode'


@bp.route('/about', methods=['GET'])
@cache.cached(timeout=50)
def about():
    print('call func')
    return g.lang_code + ' 介绍'
