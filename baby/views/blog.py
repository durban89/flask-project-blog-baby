#! _*_ coding: utf-8 _*_

from flask import (
    Blueprint, flash, g, redirect,
    request, render_template,
    url_for,
    current_app
)

from werkzeug.exceptions import abort
from baby.views.auth import login_required
from baby.db import get_db
from baby.exception import InvalidUsage

bp = Blueprint('blog', __name__, url_prefix='/post')


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    page = int(page)
    pagesize = 5

    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ' LIMIT ?, ?', ((page - 1) * pagesize, pagesize)
    ).fetchall()

    for n, p in enumerate(posts):
        o = dict(p)

        o['tag'] = db.execute(
            'SELECT name FROM tag WHERE post_id = ?', (o['id'],)).fetchall()

        current_app.logger.info(o)
        posts[n] = o

    prev_page = (page - 1) if (page - 1) else ''
    next_page = (page + 1) if len(posts) >= pagesize else ''

    return render_template('blog/index.j2',
                           posts=posts,
                           page=page,
                           prev_page=prev_page,
                           next_page=next_page,
                           pagesize=pagesize)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        date = request.form['date']
        tag = request.form['tag']
        error = None

        if not title:
            error = 'Title is required'

        if not tag:
            error = 'Tag is required'

        tags = tag.split(',')

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cur = db.cursor()
            cur.execute(
                'INSERT INTO post (title, body, author_id, the_date)'
                ' VALUES (?,?,?,?)',
                (title, body, g.user['id'], date)
            )

            db.commit()

            insert_id = cur.lastrowid

            cur.executemany(
                'INSERT INTO tag (post_id, name)'
                ' VALUES (?,?)', tag_generator(insert_id, tags)
            )

            db.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/create.j2')


def tag_generator(insert_id, tags):
    for c in tags:
        yield (insert_id, c)


def get_post(id, check_author=True):
    db = get_db()

    post = db.execute(
        'SELECT p.id, the_date, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    post = dict(post)

    tags = db.execute(
        'SELECT name FROM tag WHERE post_id = ?', (post['id'],)).fetchall()

    post['tag'] = ','.join((x['name'] for x in tags))

    current_app.logger.info(post)
    return post


@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        date = request.form['date']
        tag = request.form['tag']
        error = None

        if not title:
            error = 'Title is required'

        if not tag:
            error = 'Tag is required'

        tags = tag.split(',')

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cur = db.cursor()
            cur.execute(
                'UPDATE post SET title = ?, body = ?, the_date = ?'
                ' WHERE id = ?',
                (title, body, date, id)
            )

            db.commit()

            # 清空原来的关联
            # 建立新的关联
            #

            cur.execute(
                'DELETE FROM tag WHERE post_id = ?', (id,)
            )

            cur.executemany(
                'INSERT INTO tag (post_id, name)'
                ' VALUES (?,?)', tag_generator(id, tags)
            )

            db.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/update.j2', post=post)


@bp.route('/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute(
        'DELETE FROM post where id = ?', (id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/show', methods=['GET'])
def show(id):
    post = get_post(id, False)

    return render_template('blog/show.j2', post=post)


@bp.route('/tag/<string:name>', methods=['GET'])
def tag(name):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, p.created, author_id, username'
        ' FROM tag AS t'
        ' JOIN post AS p ON p.id = t.post_id'
        ' JOIN user u ON p.author_id = u.id'
        ' WHERE t.name = ?'
        ' ORDER BY p.created DESC', (name,)
    ).fetchall()

    for n, p in enumerate(posts):
        o = dict(p)

        o['tag'] = db.execute(
            'SELECT name FROM tag WHERE post_id = ?', (o['id'],)).fetchall()

        current_app.logger.info(o)
        posts[n] = o

        return render_template('blog/tag.j2', posts=posts)


@bp.route('/read', methods=['GET'])
def read_sum():
    raise InvalidUsage('read sum function developing...', status_code=404)
