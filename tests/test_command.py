# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-05 14:25:22
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-05 14:53:11
import pytest
import tempfile
from baby import create_app
from baby.command import create_user
from baby.command import update_user
from baby.command import create_blog
from baby.command import update_blog


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'DATABASE': db_path,
        'TESTING': True
    })

    yield app


def test_create_user(app):
    runner = app.test_cli_runner()
    result = runner.invoke(create_user, ['durban'])
    assert 'create durban' in result.output


def test_update_user(app):
    runner = app.test_cli_runner()
    result = runner.invoke(update_user, ['durban'])
    assert 'update durban' in result.output


def test_create_blog(app):
    runner = app.test_cli_runner()
    result = runner.invoke(create_blog, ['blog'])
    assert 'create blog blog' in result.output


def test_update_blog(app):
    runner = app.test_cli_runner()
    result = runner.invoke(update_blog, ['blog'])
    assert 'update blog blog' in result.output
