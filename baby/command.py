# -*- coding: utf-8 -*-
# @Author: durban.zhang
# @Date:   2019-11-05 12:07:34
# @Last Modified by:   durban.zhang
# @Last Modified time: 2019-11-05 14:48:02
import click
from flask.cli import AppGroup

user_cli = AppGroup('user')


@user_cli.command('create')
@click.argument('name')
def create_user(name):
    click.echo('create ' + name)


@user_cli.command('update')
@click.argument('name')
def update_user(name):
    click.echo('update ' + name)


blog_cli = AppGroup('blog')


@blog_cli.command('create')
@click.argument('title')
def create_blog(title):
    click.echo('create blog ' + title)


@blog_cli.command('update')
@click.argument('title')
def update_blog(title):
    click.echo('update blog ' + title)


def init_app(app):
    app.cli.add_command(user_cli)
    app.cli.add_command(blog_cli)
