#! _*_ coding: utf-8 _*_


from flask_socketio import SocketIO
from flask_caching import Cache

socketio = SocketIO(cors_allowed_origins='*')

cache = Cache()
