#! _*_ coding: utf-8 _*_
import os
import tempfile

import pytest
from baby import create_app
from baby.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):

    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test', code='1111'):
        with self._client.session_transaction() as session:
            session['captcha_key'] = '1111'

        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password,
                  'verification-code': code}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
