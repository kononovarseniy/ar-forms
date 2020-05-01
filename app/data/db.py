from contextlib import contextmanager

import psycopg2

SCHEMA_VERSION = '0.1'
SCHEMA_VERSION_PARAM = 'SCHEMA_VERSION'

DB_NAME = 'ar_forms'
DB_USER = 'ar_forms'
DB_PASS = 'master'

FORM_TYPE_POLL_ID = 1
FORM_TYPE_POLL_NAME = "poll"
FORM_TYPE_TEST_ID = 2
FORM_TYPE_TEST_NAME = "test"


def _recreate_schema():
    with open_cursor() as (conn, cur):
        cur.execute("DROP TABLE IF EXISTS paramters;")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
        cur.execute("DROP TABLE IF EXISTS form_types CASCADE;")
        cur.execute("DROP TABLE IF EXISTS forms CASCADE;")

        cur.execute("CREATE TABLE parameters (name text PRIMARY KEY, value text);")
        cur.execute("INSERT INTO parameters (name, value) VALUES (%s, %s);", (SCHEMA_VERSION_PARAM, SCHEMA_VERSION))

        cur.execute("CREATE TABLE users ("
                    "   id serial primary key,"
                    "   login text not null unique,"
                    "   display_name text not null,"
                    "   password text"
                    ");")

        cur.execute("CREATE TABLE form_types ("
                    "   id int primary key,"
                    "   name text not null"
                    ");")
        cur.execute("INSERT INTO form_types (id, name) "
                    "VALUES (%s, %s), (%s, %s)",
                    (FORM_TYPE_POLL_ID, FORM_TYPE_POLL_NAME, FORM_TYPE_TEST_ID, FORM_TYPE_TEST_NAME))

        cur.execute("CREATE TABLE forms ("
                    "   id serial primary key,"
                    "   title text not null,"
                    "   description text not null,"
                    "   type_id int not null references form_types,"
                    "   creator_id int not null references users,"
                    "   creation_date timestamp not null,"
                    "   is_public boolean not null"
                    ");")

        conn.commit()


def _get_schema_version():
    with open_cursor() as (conn, cur):
        try:
            cur.execute("SELECT value FROM parameters WHERE name = %s", (SCHEMA_VERSION_PARAM,))
            return cur.fetchone()[0]
        except psycopg2.ProgrammingError:
            return None


def _get_connection():
    """Returns connection object"""
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS)


@contextmanager
def open_cursor():
    """Context manager for connection and cursor objects"""
    connection = _get_connection()
    cursor = connection.cursor()
    try:
        yield connection, cursor
    finally:
        cursor.close()
        connection.close()


_version = _get_schema_version()
if not _version:
    _recreate_schema()
elif _version != SCHEMA_VERSION:
    raise Exception("Wrong schema version")
