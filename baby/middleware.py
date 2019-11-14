# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-13 14:20:35
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-13 14:33:33


class HTTPMethodOverrideMiddleware(object):
    allowed_methods = frozenset([
        'GET',
        'HEAD',
        'POST',
        'DELETE',
        'PUT',
        'PATCH',
        'OPTIONS'
    ])

    bodyless_methods = frozenset([
        'GET',
        'HEAD',
        'DELETE',
        'OPTIONS'
    ])

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
        if method in self.allowed_methods:
            environ['REQUEST_EMTHOD'] = method

        if method in self.bodyless_methods:
            environ['CONTENT_LENGTH'] = '0'

        return self.app(environ, start_response)
