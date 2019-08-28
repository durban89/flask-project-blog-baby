#! _*_ coding: utf-8 _*_

'''食物'''

import time
from flask import (
    Blueprint,
    jsonify,
    request,
    current_app
)
from baby.db import get_db

bp = Blueprint('api_food_type', __name__, url_prefix='/api/food')


@bp.route('/type/', methods=['GET'])
def type():
    '''food type list'''
    foodList = get_db().execute('SELECT autokid, name, sort FROM food_type '
                                'ORDER BY autokid DESC').fetchall()
    # sqlite3.Row 转化为dict
    item = []
    for x in foodList:
        item.append(dict(zip(x.keys(), x)))

    return success_json(item)


@bp.route('/type/', methods=['POST'])
def type_create():
    ''' food type create'''
    current_app.logger.info(request.form)

    formData = request.form
    if 'name' not in formData or not formData['name']:
        return fail_json(u'参数异常')

    db = get_db()
    name = formData['name']

    row = db.execute('SELECT autokid FROM food_type'
                     ' WHERE name = :name', {'name': name}).fetchone()
    if row:
        return fail_json(u'此类已存在')

    timestamp = int(time.time())
    sort = 0
    if 'sort' in formData:
        sort = int(formData['sort'])

    db.execute(
        'INSERT INTO '
        'food_type (name, sort, ctime, mtime)'
        ' VALUES (?, ?, ?, ?)',
        (name, sort, timestamp, timestamp)
    )
    db.commit()

    return success_json()


@bp.route('/type/<int:id>', methods=['GET'])
def type_detail(id):
    '''food type detail'''

    row = fetch_food_type_one_with_id(id)

    if not row:
        return fail_json('详情数据不存在')

    return success_json(dict(zip(row.keys(), row)))


@bp.route('/type/<int:id>', methods=['DELETE'])
def type_delete(id):
    ''' food type delete'''
    db = get_db()

    db.execute('DELETE FROM food_type WHERE autokid = :id', {'id': id})
    db.commit()

    return success_json()


@bp.route('/type/<int:id>', methods=['PUT'])
def type_update(id):
    ''' food type update '''

    row = fetch_food_type_one_with_id(id)

    if not row:
        return fail_json('详情数据不存在')

    formData = request.form
    if not len(formData):
        return fail_json('参数异常')

    db = get_db()

    if 'name' in formData:

        name = formData['name']

        existRow = fetch_food_type_exit_one(id, name)
        if existRow:
            return fail_json('数据已存在')

        db.execute(
            'UPDATE food_type SET name=:name WHERE autokid = :id',
            {'name': name, 'id': id}
        )

        db.commit()

    if 'sort' in formData:

        sort = formData['sort']

        db.execute(
            'UPDATE food_type SET sort=:sort WHERE autokid = :id',
            {'sort': sort, 'id': id}
        )

        db.commit()

    return success_json()


def fetch_food_type_one_with_id(id):
    row = get_db().execute(
        'SELECT * FROM food_type'
        ' WHERE autokid = :id',
        {'id': id}
    ).fetchone()

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


def fetch_food_type_one_with_name(name):
    db = get_db()
    row = db.execute('SELECT autokid FROM food_type'
                     ' WHERE name = :name', {'name': name}).fetchone()
    if not row:
        return None

    return row


def fetch_food_type_exit_one(id, name):
    db = get_db()
    row = db.execute('SELECT autokid FROM food_type'
                     ' WHERE autokid <> :id AND name = :name',
                     {'id': id, 'name': name}).fetchone()
    if not row:
        return None

    return row
