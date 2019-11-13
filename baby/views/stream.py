# -*- coding: utf-8 -*-
# @Author: durban
# @Date:   2019-11-13 11:28:21
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-13 12:05:51
from flask import (
    current_app,
    request,
    Blueprint,
    Response,
    stream_with_context
)

bp = Blueprint('stream', __name__, url_prefix='/stream')


def iter_all_rows():
    return [['1', '2', '3', '4']]


def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@bp.route('/')
def index():
    def generate():
        yield 'Hello '
        yield request.args['name'] if 'name' in request.args else 'anonymous'
        yield '!'

    return Response(stream_with_context(generate()))


@bp.route('/template')
def template():
    rows = iter_all_rows()
    return Response(stream_template('stream/template.j2', rows=rows))


@bp.route('/large.csv')
def large_csv():
    def generate():
        rows = iter_all_rows()
        for row in rows:
            yield ','.join(row) + "\n"

    return Response(generate(), mimetype='text/csv')
