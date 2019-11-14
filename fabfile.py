# -*- coding: utf-8 -*-
# @Author: durban
# @Date:   2019-11-07 21:55:23
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-11 09:36:30

from fabric import task

hosts = ["my-server"]


@task
def pack(c):
    c.run('python setup.py release sdist --format=gztar')


@task
def deploy(c):
    # TODO 远程和本地的交互问题 - 如何才能使得运行的时候正确读取本地文件然后上传的远程服务器
    result = c.run('python setup.py --fullname', hide=True)
    dist = result.stdout.strip()
    filename = '%s.tar.gz' % dist
    print(filename)
    # c.put('dist/%s' % filename, '/tmp/%s' % filename)

    # result = c.run('uname -s')
    # print(result)
