#! _*_ coding: utf-8 _*_

from setuptools import find_packages, setup

setup(
    name='baby',
    version='1.0.4',
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
