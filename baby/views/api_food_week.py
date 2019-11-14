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

bp = Blueprint('api_food_week', __name__, url_prefix='/api/food')


@bp.route('/week/', methods=['GET'])
def week():
    '''food type list'''
    foodList = get_db().execute(
        'SELECT fwl.autokid, fwl.week,'
        ' fwl.type_id, fwl.content,'
        ' ft.name as type_name'
        ' FROM food_week_list as fwl'
        ' LEFT JOIN food_type as ft ON ft.autokid = fwl.type_id'
        ' ORDER BY fwl.autokid DESC'
    ).fetchall()

    # sqlite3.Row 转化为dict
    item = []
    for x in foodList:
        item.append(dict(zip(x.keys(), x)))

    return success_json(item)


@bp.route('/week/', methods=['POST'])
def week_create():
    ''' food type create'''
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
    row = db.execute(
        'SELECT autokid FROM food_week_list'
        ' WHERE user_id =:user_id'
        ' AND week = :week'
        ' AND type_id = :type_id',
        {
            'user_id': user_id,
            'week': week,
            'type_id': type_id
        }
    ).fetchone()
    if row:
        return fail_json(u'已存在')

    timestamp = int(time.time())

    db.execute(
        'INSERT INTO'
        ' food_week_list (user_id, week, type_id, content, ctime, mtime)'
        ' VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, week, type_id, content, timestamp, timestamp)
    )
    db.commit()

    return success_json()


@bp.route('/week/<int:id>', methods=['GET'])
def week_detail(id):
    '''food type detail'''

    row = fetch_food_week_one_with_id(id)

    if not row:
        return fail_json('数据不存在')

    return success_json(dict(zip(row.keys(), row)))


@bp.route('/week/<int:id>', methods=['DELETE'])
def week_delete(id):
    ''' food type delete'''
    db = get_db()

    db.execute('DELETE FROM food_week_list WHERE autokid = :id', {'id': id})
    db.commit()

    return success_json()


@bp.route('/week/<int:id>', methods=['PUT'])
def week_update(id):
    ''' food type update '''

    row = fetch_food_week_one_with_id(id)

    if not row:
        return fail_json('详情数据不存在')

    formData = request.form

    if 'content' not in formData or not formData['content']:
        return fail_json(u'参数异常')

    content = formData['content']

    db = get_db()

    db.execute(
        'UPDATE food_week_list'
        ' SET content=:content'
        ' WHERE autokid = :id',
        {'content': content, 'id': id}
    )

    db.commit()

    return success_json()


def fetch_food_week_one_with_id(id):
    row = get_db().execute(
        'SELECT * FROM food_week_list'
        ' WHERE autokid = :id', {'id': id}).fetchone()

    if not row:
        return None

    return row


def fetch_food_type_one_with_name(name):
    db = get_db()
    row = db.execute(
        'SELECT autokid FROM food_week_list'
        ' WHERE name = :name', {'name': name}).fetchone()
    if not row:
        return None

    return row


def fetch_food_type_exit_one(id, name):
    db = get_db()
    row = db.execute(
        'SELECT autokid FROM food_week_list'
        ' WHERE autokid <> :id AND name = :name',
        {'id': id, 'name': name}).fetchone()

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
