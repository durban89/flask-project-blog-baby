#! _*_ coding: utf-8 _*_
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')


@click.command('execute-db-sql')
@click.option("--sql", default="", help="SQLite sql string.")
@with_appcontext
def execute_db_sql(sql):
    '''Execute db sql'''
    if not sql:
        click.echo('Empty SQL')
        return

    db = get_db()

    db.execute(sql)
    db.commit()
    click.echo('Execute success.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(execute_db_sql)
