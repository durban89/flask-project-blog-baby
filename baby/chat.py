#! _*_ coding: utf-8 _*_
#
#

import random
import functools

from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    g,
    session
)
from baby.extensions import socketio
from flask_socketio import (
    emit,
    join_room,
    leave_room,
    close_room,
    rooms,
    disconnect
)

online_nicks = []
online_sid = []
online_sid_dict = {}
online_num = 0

bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/', methods=['GET'])
def index():
    colors = ['#FF5370', '#F07178',
              '#F78C6C', '#FFCB6B',
              '#FFB62C', '#C3E88D',
              '#91B859', '#B2CCD6',
              '#8796B0', '#89DDFF',
              '#39ADB5', '#82AAFF',
              '#6182B8', '#C792EA',
              '#7C4DFF', '#BB80B3',
              '#945EB8', '#AB7967',
              '#AB7967', '#E53935'
              ]
    color = random.choice(colors)
    return render_template('/chat/index.j2', avatar_bg_color=color)


def authenticated(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # 授权判断
        user_id = session.get('user_id', 0)
        if user_id == 0:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('connect', namespace='/chat')
@authenticated
def handle_connect():
    emit('response', {
        'data': 'Connected',
        'type': 'tips'
    })


@socketio.on('message', namespace='/chat')
@authenticated
def handle_message(message):
    # 信息发到服务器进行过滤

    emit('response', message)


@socketio.on('broadcast_event', namespace='/chat')
@authenticated
def handle_broadcast_event(msg):
    global online_num
    nick = None
    avatar_bg_color = 'grey'

    if 'nick' in msg:
        nick = msg['nick']

    if 'avatar_bg_color' in msg:
        avatar_bg_color = msg['avatar_bg_color']

    if nick is not None:
        if nick in online_nicks and request.sid not in online_sid:
            emit('error', {
                'data': '昵称已经存在',
                'type': 'alert'
            })
            return True
        elif request.sid in online_sid_dict and online_sid_dict[request.sid] != nick:
            emit('error', {
                'data': '不能更换昵称',
                'type': 'alert'
            })
            return True
        else:
            if request.sid not in online_sid:
                online_num += 1
                session['nick'] = nick

                online_nicks.append(nick)
                online_sid.append(request.sid)

                online_sid_dict[request.sid] = nick

        nick = nick[:1]
        emit('response', {
            'data': msg['data'],
            'type': msg['type'],
            'nick': nick,
            'avatar_bg_color': avatar_bg_color,
            'online_num': online_num
        }, broadcast=True)


@socketio.on('event', namespace='/chat')
@authenticated
def handle_event(msg):
    emit('response', {'data': msg['data'], 'type': msg['type']})


@socketio.on('ping', namespace='/chat')
@authenticated
def ping_pong():
    emit('pong')


@socketio.on('join', namespace='/chat')
@authenticated
def hanle_join(message):
    emit('response', {
        'data': 'In Rooms',
        'type': 'tips',
    })


@socketio.on('leave', namespace='/chat')
@authenticated
def handle_leave(message):
    emit('response', {
        'data': 'Out Rooms',
        'type': 'tips',
    })


@socketio.on('disconnect', namespace='/chat')
@authenticated
def handle_disconnect():
    global online_num
    nick = session.get('nick')
    if request.sid in online_sid_dict:
        online_num -= 1
        if online_num <= 0:
            online_num = 0

        del online_sid_dict[request.sid]
        online_nicks.remove(session['nick'])

    print('Client Disconnect', request.sid)

    emit('response', {
        'data': session['nick'] + 'Client Disconnect',
        'type': 'tips',
        'online_num': online_num
    }, broadcast=True)


@socketio.on_error('/chat')  # handles the '/chat' namespace
def error_handler_chat(e):
    print(e)
    pass


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass
