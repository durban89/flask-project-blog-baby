#! _*_ coding: utf-8 _*_

import pytest

from flask import g, session
from baby.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )

    assert b'Username is invalidate.' in response.data

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'"
        ).fetchone() is None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Username is invalidate.'),
    ('test', 'test', b'Username has been registered.'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )

    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    with client.session_transaction() as session:
        session['captcha_key'] = '1111'
        session['user_id'] = 1

    response = auth.login(username='test', password='test', code='1111')

    assert 'http://localhost/post/' == response.headers['Location']

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()
    with client:
        auth.logout()
        assert 'user_id' not in session
