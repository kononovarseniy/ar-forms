import psycopg2

from data.db import get_cursor, del_cursor
from data.entities import User


class UserRepository:
    @staticmethod
    def get_user_by_id(user_id):
        conn, cur = get_cursor()
        cur.execute('SELECT id, login, display_name FROM users WHERE id = %s;', (user_id,))
        user_fields = cur.fetchone()
        del_cursor(conn, cur)
        if user_fields:
            return User(*user_fields)

    @staticmethod
    def add_user(login, display_name, password):
        conn, cur = get_cursor()
        try:
            cur.execute(
                "INSERT INTO users (login, display_name, password) "
                "VALUES (%s, %s, crypt(%s, gen_salt('md5'))) RETURNING id;",
                (login, display_name, password))
            conn.commit()
            user_id, = cur.fetchone()
        except psycopg2.IntegrityError:
            return None
        finally:
            del_cursor(conn, cur)

        return User(user_id, login, display_name)

    @staticmethod
    def get_user_by_credentials(login, password):
        conn, cur = get_cursor()
        cur.execute('SELECT id, login, display_name FROM users '
                    'WHERE login = %s AND password = crypt(%s, password);', (login, password))
        user_fields = cur.fetchone()
        del_cursor(conn, cur)

        if user_fields:
            return User(*user_fields)
