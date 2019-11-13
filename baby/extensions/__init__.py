#! _*_ coding: utf-8 _*_


from flask_socketio import SocketIO
from flask_caching import Cache
from flask_mongoengine import MongoEngine

socketio = SocketIO(cors_allowed_origins='*')

cache = Cache()

mongodb = MongoEngine()
