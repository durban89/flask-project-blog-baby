# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-12-05 18:30:44
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-12-05 18:46:49

from flask import session
from werkzeug.security import check_password_hash

# with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
#     _data_sql = f.read().decode('utf8')


# @pytest.fixture
# def client():
#     db_fd, db_path = tempfile.mkstemp()

#     app = create_app({
#         'DATABASE': db_path,
#         'TESTING': True
#     })

#     client = app.test_client()

#     with app.app_context():
#         init_db()
#         get_db().executescript(_data_sql)

#     yield client

#     os.close(db_fd)
#     os.unlink(app.config['DATABASE'])


def test_empty_db(client):
    rv = client.get('/')
    assert b'Baby' in rv.data


# class AuthActions(object):

#     def __init__(self, client):
#         self._client = client

#     def login(self, username='test', password='test'):
#         return self._client.post(
#             '/auth/login',
#             data={'username': username, 'password': password},
#             follow_redirects=True
#         )

#     def logout(self):
#         return self._client.get('/auth/logout', follow_redirects=True)


def test_login(client, auth):
    auth.login()
    with client:
        client.get('/')
        assert session['user_id'] == 1

    rv = auth.login('testx', 'test')
    print(rv.data)
    assert b'Incorrect username' in rv.data

    rv = auth.login('test', 'testx')
    print(rv.data)
    assert b'Incorrect password' in rv.data


def test_logout(client, auth):
    auth.login('test', 'test')
    with client:
        auth.logout()
        assert 'user_id' not in session


def test_add_post(client, auth):
    auth.login()

    with client:
        rv = client.post('/post/create', data=dict(
            title='<Hello>',
            body='<strong>Html</strong> is here',
            tag='html',
            date='2019-12-05',
            category_id=1
        ), follow_redirects=True)

        print(rv.data)
        assert b'<strong>Html</strong> is here' in rv.data

        assert b'<Hello>' in rv.data


def test_api_auth(app):
    with app.test_client() as c:
        rv = c.post('/api/auth', json={
            'email': 'flask', 'password': 'secret'
        })
        json_data = rv.get_json()
        assert check_password_hash(json_data['token'], 'secret')
