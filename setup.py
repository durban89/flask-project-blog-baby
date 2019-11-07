# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-10-21 13:35:26
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-06 17:17:36

from setuptools import find_packages, setup

setup(
    name='baby',
    version='1.0.6',
    author='张大鹏',
    author_email='durban.zhang@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-socketio',
        'gunicorn[eventlet]'
    ]
)
