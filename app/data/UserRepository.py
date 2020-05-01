import psycopg2

from data.db import open_cursor
from data.entities import User
from data.fieldset import EntityFields


class UserRepository:
    fields = EntityFields(['id', 'login', 'display_name'], User, 'users')

    @staticmethod
    def get_user_by_id(user_id):
        with open_cursor() as (conn, cur):
            cur.execute('SELECT id, login, display_name FROM users WHERE id = %s;', (user_id,))
            user_fields = cur.fetchone()
        if user_fields:
            return User(*user_fields)

    @staticmethod
    def add_user(login, display_name, password):
        with open_cursor() as (conn, cur):
            try:
                cur.execute(
                    "INSERT INTO users (login, display_name, password) "
                    "VALUES (%s, %s, crypt(%s, gen_salt('md5'))) RETURNING id;",
                    (login, display_name, password))
                user_id, = cur.fetchone()
                conn.commit()
                return User(user_id, login, display_name)
            except psycopg2.IntegrityError:
                return None

    @staticmethod
    def get_user_by_credentials(login, password):
        with open_cursor() as (conn, cur):
            cur.execute('SELECT id, login, display_name FROM users '
                        'WHERE login = %s AND password = crypt(%s, password);', (login, password))
            user_fields = cur.fetchone()

        if user_fields:
            return User(*user_fields)
