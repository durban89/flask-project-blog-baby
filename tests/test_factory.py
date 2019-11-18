#! _*_ coding: utf-8 _*_

from baby import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_baby(client):
    response = client.get('/baby')
    assert response.data == b'Baby'
