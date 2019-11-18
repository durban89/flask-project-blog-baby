#! _*_ coding: utf-8 _*_

import os

from flask import (
    Flask,
    jsonify
)

from logging.config import dictConfig
from baby.extensions import socketio, mail
from baby import command
from baby import views
from baby import db
from baby_backend import application as backend
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import BadRequest
from baby.exception import InvalidUsage
from baby.middleware import HTTPMethodOverrideMiddleware
from baby.helper import (
    register_cache,
    register_mail,
    register_mongodb,
    register_sentry
)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # middleware

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
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

    # upload config
    app.config['UPLOAD_DIR'] = os.path.join(os.getcwd(), 'uploads')
    app.config['UPLOAD_ALLOWED_EXTENSIONS'] = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'
    }
    app.config['UPLOAD_MAX_LENGTH'] = 1 * 1024 * 1024  # 1M

    # mongodb config
    app.config['MONGODB_SETTINGS'] = {
        'db': 'baby',
        'alias': 'default'
    }

    # celery config
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

    # flask-mail config
    if 'MAIL_HOST' in app.config:
        app.config['MAIL_SERVER'] = app.config['MAIL_HOST']

    if 'MAIL_FROM' in app.config:
        app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_FROM']

    try:
        os.makedirs(app.config['UPLOAD_DIR'])
    except OSError:
        pass

    # Register Extensions
    if app.debug:
        socketio.init_app(app, logger=True, engineio_logger=True)
    else:
        socketio.init_app(app)

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

    command.init_app(app)
    views.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    if not app.debug:
        register_mail(app)
        register_sentry(app)

    register_cache(app)
    register_mongodb(app)

    # 整合baby_backend
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/backend': backend
    })

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return 'bad request!', 400

    # 自定义制定状态码的处理逻辑
    @app.errorhandler(404)
    def handle_bad_404_request(e):
        return '404 bad request!', 400

    # 注册自定义异常
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(e):
        response = jsonify(e.to_dict())
        print(response)
        return response

    return app


application = create_app()

if __name__ == "__main__":
    socketio.run(application, debug=application.debug)
