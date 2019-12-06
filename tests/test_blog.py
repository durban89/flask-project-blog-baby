#! _*_ coding: utf-8 _*_

import pytest
from baby.db import get_db


def test_index(client, auth):
    response = client.get('/post/')
    assert b'Log In' in response.data
    assert b'Register' in response.data

    auth.login()
    response = client.get('/post/')

    print(response.data)
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/post/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/post/create',
    '/post/1/update',
    '/post/1/delete'
))
def test_login_required(client, path):
    response = client.post(path)
    assert 'http://localhost/auth/login' == response.headers['Location']


def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute(
            'UPDATE post SET author_id = 2 WHERE id = 1'
        )
        db.commit()

    auth.login()

    assert client.post('/post/1/update').status_code == 403
    assert client.post('/post/1/delete').status_code == 403

    assert b'href="/post/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    ('/post/2/update'),
    ('/post/2/delete')
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/post/create').status_code == 200

    client.post('/post/create', data={
        'title': 'created',
        'body': 'created',
        'date': '2019-12-06',
        'tag': 'created',
        'category_id': 1,
    })

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(app, client, auth):
    auth.login()
    assert client.get('/post/1/update').status_code == 200
    client.post('/post/1/update', data={
        'title': 'updated',
        'body': 'updated',
        'date': '2019-12-06',
        'tag': 'created',
        'category_id': 1,
    })

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/post/create',
    '/post/1/update'
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    print(response.data)
    assert b'Title is required' in response.data


def test_delete(app, client, auth):
    auth.login()
    response = client.post('/post/1/delete')
    assert response.headers['Location'] == 'http://localhost/post/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
