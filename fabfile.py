# -*- coding: utf-8 -*-
# @Author: durban
# @Date:   2019-11-07 21:55:23
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-12-05 16:37:34

import getpass
from fabric import Connection, task


@task
def pack(c):
    c.run('python setup.py release sdist --format=gztar')


@task
def deploy(c):
    user = input('Input login user name: ')

    host = input('Input login host: ')

    root = input('Input project root path：')

    user_pass = getpass.getpass('Input login user pass：')

    result = c.run('python setup.py --fullname', hide=True)
    dist = result.stdout.strip()
    filename = '%s.tar.gz' % dist

    result = c.run('python setup.py --name', hide=True)
    name = result.stdout.strip()

    remote = Connection('%s@%s' % (user, host),
                        connect_kwargs={"password": user_pass})

    remote.run('cd %s && ls -al' % root)
    return False

    remote.put('./dist/%s' %
               filename, remote='%s' % root)

    remote.run('cd %s &&\
     source .env/bin/activate &&\
        ls -al && type python &&\
         pip install %s &&\
         supervisorctl restart %s' % (root, filename, name))
