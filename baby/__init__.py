#! _*_ coding: utf-8 _*_

import os
import logging

from flask import (
    Flask,
    has_request_context,
    request
)
from raven.contrib.flask import Sentry
from logging.config import dictConfig
from logging.handlers import SMTPHandler
from baby.extensions import socketio
from baby import command


def error_handler(e):
    return 'bad bad bad request!', 400


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

# 添加mail Handler


def register_mail_handler(app):
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


def register_sentry(app):
    if 'SENTRY_DSN' in app.config and app.config['SENTRY_DSN']:
        sentry = Sentry(dsn=app.config['SENTRY_DSN'])
        sentry.init_app(app)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # if not app.debug:

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'baby.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Error Handler
    app.register_error_handler(400, error_handler)

    # Register Extensions
    if app.debug:
        socketio.init_app(app, logger=True, engineio_logger=True)
    else:
        socketio.init_app(app)

    command.init_app(app)

    # config logger
    if not app.debug:
        dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s \
            in %(module)s: %(message)s ',
                }
            },
            'handlers': {
                'wsgi': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://flask.logging.wsgi_errors_stream',
                    'formatter': 'default'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['wsgi']
            }
        })

    from . import db
    db.init_app(app)

    from . import home
    app.register_blueprint(home.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import food
    app.register_blueprint(food.bp)

    from . import chat
    app.register_blueprint(chat.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    from . import api_food
    app.register_blueprint(api_food.bp)

    from . import api_food_type
    app.register_blueprint(api_food_type.bp)

    from . import api_food_week
    app.register_blueprint(api_food_week.bp)

    from . import api_auth
    app.register_blueprint(api_auth.bp)

    if not app.debug:
        # SMTP
        register_mail_handler(app)
        # Sentry
        register_sentry(app)

    return app


application = create_app()

if __name__ == "__main__":
    socketio.run(application, debug=application.debug)
