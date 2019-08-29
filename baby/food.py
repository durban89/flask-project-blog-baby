#! _*_ coding: utf-8 _*_

'''食物'''

import time
from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
    render_template,
    g,
    flash,
    redirect,
    url_for
)
from baby.db import get_db

bp = Blueprint('food', __name__, url_prefix='/food')

WEEK = {
    '1': {
        'name': u'周一',
        'food': []
    },
    '2': {
        'name': u'周二',
        'food': []
    },
    '3': {
        'name': u'周三',
        'food': []
    },
    '4': {
        'name': u'周四',
        'food': []
    },
    '5': {
        'name': u'周五',
        'food': []
    },
    '6': {
        'name': u'周六',
        'food': []
    },
    '7': {
        'name': u'周日',
        'food': []
    },
}


@bp.route('/', methods=['GET'])
def index():
    '''food list'''
    user_id = g.user['id']
    weeks = WEEK

    types = get_food_type()

    for week in weeks:
        weeks_food = get_data_with_week(week, user_id)
        for type_id in types:
            if type_id not in weeks_food:
                food = get_data_from_list_with_week(week, type_id, user_id)
                if food:
                    weeks_food[type_id] = food['content']
                else:
                    weeks_food[type_id] = ''

        weeks[week]['food'] = weeks_food

    return render_template('food/index.j2', weeks=weeks, types=types)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    ''' food create'''
    if request.method == 'POST':
        user_id = g.user['id']

        type_id = request.form['type_id']
        content = request.form['content']
        error = None

        if not type_id:
            error = 'Type is required'
        elif not content:
            error = 'Content is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            dt = datetime.today()
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
                flash('今天的已添加')
            else:
                timestamp = int(time.time())

                db.execute(
                    'INSERT INTO'
                    ' food_list (user_id,'
                    ' week, type_id, the_date, content, ctime, mtime)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (user_id, week, type_id, the_date,
                     content, timestamp, timestamp)
                )
                db.commit()

                return redirect(url_for('food.index'))

    types = get_food_type()

    current_app.logger.info(types)

    return render_template('food/create.j2', types=types)


@bp.route('/<int:id>', methods=['GET'])
def type_detail(id):
    '''food detail'''

    row = fetch_food_one_with_id(id)

    if not row:
        return fail_json('详情数据不存在')

    return success_json(dict(zip(row.keys(), row)))


@bp.route('/<int:id>', methods=['DELETE'])
def type_delete(id):
    ''' food delete'''
    db = get_db()

    db.execute('DELETE FROM food_list WHERE autokid = :id', {'id': id})
    db.commit()

    return success_json()

# TODO


@bp.route('/<int:id>', methods=['PUT'])
def type_update(id):
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


@bp.route('/week/<int:week>/<int:type_id>', methods=['GET', 'POST'])
def week_update(week, type_id):
    '''更新'''
    user_id = g.user['id']

    content = ''
    is_new = False

    week_data = get_data_with_week_type(week, type_id, user_id)

    if week_data is None:
        food_data = get_data_from_list_with_week(week, type_id, user_id)
        if food_data:
            content = food_data['content']
    else:
        is_new = True
        content = week_data['content']

    if request.method == 'POST':
        if len(request.form) > 0 \
                and 'content' in request.form \
                and request.form['content']:
            db = get_db()
            db.execute()
            db.commit()

        redirect(url_for('food.index'))

    types = get_food_type()

    renderData = {}
    renderData['content'] = content
    renderData['is_new'] = is_new
    renderData['week_name'] = WEEK[str(week)]['name']
    renderData['type_name'] = types[type_id]['name']

    current_app.logger.info(renderData)

    return render_template('food/week_update.j2', renderData=renderData)


def get_food_type():
    rows = get_db().execute(
        'SELECT autokid, name FROM food_type '
        ' ORDER BY sort ASC').fetchall()

    types = {}

    for row in rows:
        tmp = dict(zip(row.keys(), row))
        types[tmp['autokid']] = tmp

    return types


def get_data_from_list_with_week(week, type_id, user_id):
    row = get_db().execute(
        'SELECT content FROM food_list '
        ' WHERE week = :week'
        ' AND user_id = :user_id'
        ' AND type_id = :type_id'
        ' ORDER BY autokid DESC LIMIT 0,1',
        {
            'week': week,
            'type_id': type_id,
            'user_id': user_id
        }
    ).fetchone()

    if row:
        row = dict(zip(row.keys(), row))

        return row

    return None


def get_data_with_week_type(week, type_id, user_id):
    row = get_db().execute(
        'SELECT * FROM food_week_list'
        ' WHERE week = :week'
        ' AND user_id = :user_id'
        ' AND type_id = :type_id',
        {
            'week': week,
            'type_id': type_id,
            'user_id': user_id,
        }
    ).fetchone()

    if row:
        return dict(zip(row.keys(), row))

    return None


def get_data_with_week(week, user_id):
    rows = get_db().execute(
        'SELECT * FROM food_week_list '
        ' WHERE week = :week'
        ' AND user_id = :user_id',
        {'week': week, 'user_id': user_id}).fetchall()

    weeks_food = {}
    for row in rows:
        tmp = dict(zip(row.keys(), row))
        weeks_food[tmp['type_id']] = tmp['content']

    return weeks_food
