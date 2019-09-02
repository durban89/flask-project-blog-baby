#! _*_ coding: utf-8 _*_

'''食物'''

import time
from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    request,
    current_app
)
from baby.db import get_db

bp = Blueprint('api_food', __name__, url_prefix='/api/food')


@bp.route('/', methods=['GET'])
def index():
    '''food list'''
    foodList = get_db().execute(
        'SELECT * FROM food_list '
        'ORDER BY autokid DESC').fetchall()

    # sqlite3.Row 转化为dict
    item = []
    for x in foodList:
        item.append(dict(zip(x.keys(), x)))

    return success_json(item)


@bp.route('/', methods=['POST'])
def create():
    ''' food create'''
    user_id = 1

    current_app.logger.info(request.form)

    formData = request.form
    if 'type_id' not in formData or not formData['type_id']:
        return fail_json(u'参数异常')

    if 'content' not in formData or not formData['content']:
        return fail_json(u'参数异常')

    db = get_db()

    dt = datetime.today()
    type_id = formData['type_id']
    content = formData['content']
    week = dt.weekday() + 1
    the_date = int(dt.strftime("%Y%m%d"))

    row = db.execute(
        'SELECT autokid FROM food_list'
        ' WHERE user_id =:user_id'
        ' AND the_date = :the_date'
        ' AND type_id = :type_id',
        {
            'user_id': user_id,
            'the_date': the_date,
            'type_id': type_id
        }
    ).fetchone()

    if row:
        return fail_json(u'已存在')

    timestamp = int(time.time())

    db.execute(
        'INSERT INTO'
        ' food_list (user_id, week, type_id, the_date, content, ctime, mtime)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, week, type_id, the_date, content, timestamp, timestamp)
    )
    db.commit()

    return success_json()


@bp.route('/<int:id>', methods=['GET'])
def detail(id):
    '''food detail'''

    row = fetch_food_one_with_id(id)

    if not row:
        return fail_json('详情数据不存在')

    return success_json(dict(zip(row.keys(), row)))


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    ''' food delete'''
    db = get_db()

    db.execute('DELETE FROM food_list WHERE autokid = :id', {'id': id})
    db.commit()

    return success_json()

# TODO


@bp.route('/<int:id>', methods=['PUT'])
def update(id):
    ''' food type update '''

    row = fetch_food_one_with_id(id)

    if not row:
        return fail_json('详情数据不存在')

    formData = request.form
    if 'content' not in formData:
        return fail_json('参数异常')

    content = formData['content']

    db = get_db()

    db.execute(
        'UPDATE food_type SET content=:content WHERE autokid = :id',
        {'content': content, 'id': id}
    )

    db.commit()

    return success_json()


def fetch_food_one_with_id(id):
    row = get_db().execute('SELECT * FROM food_list'
                           ' WHERE autokid = :id', {'id': id}).fetchone()

    if not row:
        return None

    return row


def success_json(o={}):
    data = {}
    data['status'] = True
    data['message'] = ''
    data['code'] = ''
    data['data'] = o
    return jsonify(data)


def fail_json(message='', code='', o={}):
    data = {}
    data['status'] = False
    data['message'] = message
    data['code'] = ''
    data['data'] = o
    return jsonify(data)
