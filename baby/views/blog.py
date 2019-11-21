# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-11 11:25:10
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-21 12:13:44

import os
from flask import (
    Blueprint, flash, g, redirect,
    request, render_template,
    url_for,
    current_app,
    send_from_directory
)

from werkzeug import secure_filename
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
        'SELECT p.id, pc.category_id, c.name AS category_name,'
        ' p.title, p.body, p.created, p.author_id, u.username'
        ' FROM post p'
        ' JOIN user u ON p.author_id = u.id'
        ' JOIN post_category pc ON pc.post_id = p.id'
        ' JOIN category c ON c.id = pc.category_id'
        ' ORDER BY p.created DESC'
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
        category_id = request.form[
            'category_id'] if 'category_id' in request.form else ''
        error = None

        if not title:
            error = 'Title is required'

        if not category_id:
            error = 'Category is required'

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

            # tag insert
            insert_id = cur.lastrowid

            cur.executemany(
                'INSERT INTO tag (post_id, name)'
                ' VALUES (?,?)', tag_generator(insert_id, tags)
            )

            db.commit()

            # category insert
            cur.execute(
                'INSERT INTO post_category (post_id, category_id)'
                ' VALUES (?,?)',
                (insert_id, category_id)
            )

            db.commit()

            return redirect(url_for('blog.index'))

    category = get_category()

    return render_template(
        'blog/create.j2',
        category=category
    )


def tag_generator(insert_id, tags):
    for c in tags:
        yield (insert_id, c)


def get_category():
    db = get_db()
    category = db.execute('SELECT * FROM category ORDER BY id DESC').fetchall()

    return category


def get_post(id, check_author=True):
    db = get_db()

    post = db.execute(
        'SELECT p.id, pc.category_id,'
        ' the_date, title, body, p.created, author_id, username'
        ' FROM post p'
        ' JOIN user u ON p.author_id = u.id'
        ' JOIN post_category pc ON pc.post_id = p.id'
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
        category_id = request.form['category_id']
        error = None

        if not title:
            error = 'Title is required'

        if not category_id:
            error = 'Category is request'

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

            cur.execute(
                'UPDATE post_category SET category_id = ?'
                ' WHERE post_id = ?',
                (category_id, id,))

            db.commit()

            return redirect(url_for('blog.index'))

    category = get_category()

    return render_template(
        'blog/update.j2',
        post=post,
        category=category
    )


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


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config[
            'UPLOAD_ALLOWED_EXTENSIONS']


def allowed_length(length):
    return length <= current_app.config[
        'UPLOAD_MAX_LENGTH']


@bp.route('/icon', methods=['GET', 'POST'])
@login_required
def icon():
    if request.method == 'POST':
        print(request.files)
        if 'icon' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['icon']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and \
                allowed_file(file.filename) and \
                allowed_length(file.content_length):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_DIR'], filename))
            return redirect(url_for('blog.uploaded_icon', filename=filename))
    else:
        return render_template('blog/icon.j2')


@bp.route('/uploaded/icon/<string:filename>', methods=['GET'])
def uploaded_icon(filename):
    return send_from_directory(current_app.config['UPLOAD_DIR'], filename)
