import os
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from api import fetch_areas

DATA_BASE_FILE_NAME = 'app.sqlite'
DATA_BASE_SCHEMA_FILE_NAME = 'schema.sql'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            os.path.join(current_app.root_path, DATA_BASE_FILE_NAME),
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
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def db_seed():
    click.echo('Fetch areas.')
    areas = fetch_areas()

    click.echo('Seed areas.')
    db = get_db()
    cursor = db.cursor()

    cursor.executemany(
        'INSERT INTO area (id, name) VALUES (?, ?);',
        list(
            map(
                lambda a: (int(a.get('id')), a.get('name')),
                areas
            )
        )
    )

    cursor.executemany(
        'INSERT INTO area_parent_area (area_id, parent_area_id) VALUES (?, ?);',
        list(
            map(
                lambda a: (int(a.get('id')), int(a.get('parent_id'))),
                filter(lambda a: a.get('parent_id'), areas)
            )
        )
    )

    db.commit()


@click.command('db-seed')
@with_appcontext
def db_seed_command():
    """Seed database tables with data from hh.ru."""
    db_seed()
    click.echo('DB seeded.')


def get_areas():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name FROM area;')
    return cursor.fetchall()


def get_area_by_id(area_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name FROM area WHERE id == ?;', area_id)
    return cursor.fetchone()
