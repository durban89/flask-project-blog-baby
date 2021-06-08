# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-10-21 13:35:26
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-12-06 10:58:27

from setuptools import find_packages, setup

setup(
    name='baby',
    version='1.0.18',
    author='张大鹏',
    author_email='durban.zhang@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask==1.1.1',
        'Flask-SocketIO==4.2.1',
        'Flask-Caching==1.7.2',
        'Flask-WTF==0.14.2',
        'Flask-Mail==0.9.1',
        'Pillow==8.2.0',
        'flask-mongoengine==0.9.5',
        'gunicorn[eventlet]==20.0.3',
        'raven[flask]',
        'celery==4.3.0',
        'redis==3.3.11'
    ]
)
