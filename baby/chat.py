#! _*_ coding: utf-8 _*_
#
#

from flask import Blueprint, render_template, request, current_app
from baby.extensions import socketio
from flask_socketio import emit


bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/', methods=['GET'])
def index():
    return render_template('/chat/index.j2')


@socketio.on('connect', namespace='/chat')
def handle_connect():
    emit('my_response', {'data': 'Connected', 'type': 'tips'})


@socketio.on('message', namespace='/chat')
def handle_message(message):
    emit('my_response', message)


@socketio.on('my_event', namespace='/chat')
def handle_event(msg):
    emit('my_response', {'data': msg['data'], 'type': msg['type']})


@socketio.on('my_ping', namespace='/chat')
def ping_pong():
    print('ping_pong')
    emit('my_pong')


@socketio.on('join', namespace='/chat')
def join(message):
    emit('my_response', {'data': 'In Rooms', 'type': 'tips'})


@socketio.on('leave', namespace='/chat')
def leave(message):
    emit('my_response', {'data': 'Out Rooms', 'type': 'tips'})


@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('Client Disconnect', request.sid)


@socketio.on_error('/chat')  # handles the '/chat' namespace
def error_handler_chat(e):
    print(e)
    pass


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass
