from contextlib import contextmanager
from typing import Optional

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
    with open_cursor() as cur:
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


def _get_schema_version():
    with open_cursor() as cur:
        try:
            cur.execute("SELECT value FROM parameters WHERE name = %s", (SCHEMA_VERSION_PARAM,))
            return cur.fetchone()[0]
        except psycopg2.ProgrammingError:
            return None


class Transaction:
    """Represents current transaction"""

    def __init__(self, connection):
        """Do not use directly. Use Transaction.open instead."""
        self._connection = connection

    @staticmethod
    @contextmanager
    def open():
        """Open new transaction. Does nothing if transaction already open."""
        global current_transaction

        if current_transaction:
            yield current_transaction
        else:
            try:
                conn = get_connection(True)
                current_transaction = Transaction(conn)
                yield current_transaction
            finally:
                current_transaction = None

    @property
    def connection(self):
        """Connection corresponding to current transaction"""
        return self._connection

    def commit(self):
        """Commit transaction. And start next transaction"""
        self.connection.commit()

    def rollback(self):
        """Rollback transaction. And start next transaction"""
        self.connection.rollback()


current_transaction: Optional[Transaction] = None


def get_connection(new: bool = False):
    """
    Returns connection object.
    :param new: if it is False (default) and there is open transaction,
    then connection corresponding to current transaction is returned.
    Otherwise new connection is created.
    :return: psycopg2 connection
    """
    if not new and current_transaction is not None:
        return current_transaction.connection
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS)


@contextmanager
def open_cursor(new_transaction: bool = False):
    """
    Context manager for db cursor.
    New transaction is created when either new_transaction is True or there is no currently open transaction.
    If new transaction is created it will be committed at exit if no error occurred and closed in any case.
    If there is open transaction it will not be committed or closed at exit.
    :param new_transaction: Force transaction creation
    :return: Cursor object associated with transaction
    """
    in_transaction = not new_transaction and current_transaction is not None
    if in_transaction:
        connection = current_transaction.connection
    else:
        connection = get_connection(True)
    with connection.cursor() as cursor:
        try:
            yield cursor
            if not in_transaction:
                connection.commit()
        finally:
            if not in_transaction:
                connection.close()


_version = _get_schema_version()
if not _version:
    _recreate_schema()
elif _version != SCHEMA_VERSION:
    raise Exception("Wrong schema version")
