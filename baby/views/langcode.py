# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-11 12:00:49
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-12 11:47:12

from flask import (
    Blueprint,
    g,
    request
)
from baby.extensions import cache
from baby.decorator import templated, cached


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
