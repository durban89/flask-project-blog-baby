#! _*_ coding: utf-8 _*_


from flask_socketio import SocketIO
from flask_caching import Cache
from flask_mongoengine import MongoEngine
from flask_mail import Mail

socketio = SocketIO(cors_allowed_origins='*')

cache = Cache()

mongodb = MongoEngine()

mail = Mail()
