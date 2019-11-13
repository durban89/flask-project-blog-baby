# -*- coding: utf-8 -*-
# @Author: durban
# @Date:   2019-11-07 21:55:23
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-08 09:37:16

from fabric.api import (
    env,
    local,
    put,
    run
)

env.user = 'durban'

env.hosts = ['127.0.0.1']


def pack():
    local('python setup.py sdist --format=gztar', capture=True)


def deploy():
    dist = local('python setup.py --fullname', capture=True).strip()
    filename = '%s.tar.gz' % dist

    put('dist/%s' % filename, '/tmp/%s' % filename)

    run('/Users/durban/python/walkerfree_pip/.env3_baby/bin/pip\
     install /tmp/%s' % filename)
    run('rm -r /tmp/%s' % filename)
    run('supervisorctl -c /usr/local/etc/supervisord.ini\
     -u admin -p 123456 restart baby_test')
