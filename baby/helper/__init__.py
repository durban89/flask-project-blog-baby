# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-14 14:13:19
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-14 14:14:05

import hashlib
import logging
from flask import has_request_context, request
from logging.handlers import SMTPHandler
from baby.extensions import cache, mongodb
from raven.contrib.flask import Sentry
from werkzeug.utils import import_string, cached_property


def logging_common_formatter():
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            if has_request_context():
                record.url = request.url
                record.remote_addr = request.remote_addr
            else:
                record.url = None
                record.remote_addr = None

            return super().format(record)

    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    return formatter


def register_mail(app):
    # SMTP Handler
    if 'MAIL_HOST' in app.config and app.config['MAIL_HOST']\
            and 'MAIL_PORT' in app.config and app.config['MAIL_PORT']\
            and 'MAIL_FROM' in app.config and app.config['MAIL_FROM']\
            and 'MAIL_TO' in app.config and app.config['MAIL_TO']\
            and 'MAIL_USERNAME' in app.config and app.config['MAIL_USERNAME']\
            and 'MAIL_PASSWORD' in app.config and app.config['MAIL_PASSWORD']:

        mail_handler = SMTPHandler(
            (
                app.config['MAIL_HOST'],
                app.config['MAIL_PORT'],
            ),
            app.config['MAIL_FROM'],
            app.config['MAIL_TO'],
            'Application Error',
            (
                app.config['MAIL_USERNAME'],
                app.config['MAIL_PASSWORD'],
            )
        )

        mail_handler.setLevel(logging.ERROR)
        formatter = logging_common_formatter()

        mail_handler.setFormatter(formatter)

        app.logger.addHandler(mail_handler)

        logging.info('register mail handler success')


def register_cache(app):
    if 'CACHE_TYPE' in app.config and app.config['CACHE_TYPE']:
        cache.init_app(app, config={
            'CACHE_TYPE': app.config['CACHE_TYPE']
        })


def register_mongodb(app):
    mongodb.init_app(app)


def register_sentry(app):
    if 'SENTRY_DSN' in app.config and app.config['SENTRY_DSN']:
        sentry = Sentry(dsn=app.config['SENTRY_DSN'])
        sentry.init_app(app)


class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


class ChecksumCalcStream(object):

    def __init__(self, stream):
        self._stream = stream
        self._hash = hashlib.sha1()

    def read(self, bytes):
        rv = self._stream.read(bytes)
        self._hash.update(rv)
        return rv

    def readline(self, size_hint):
        rv = self._stream.readline(size_hint)
        self._hash.update(rv)
        return rv


def generate_checksum(request):
    env = request.environ
    stream = ChecksumCalcStream(env['wsgi.input'])
    env['wsgi.input'] = stream
    return stream._hash
