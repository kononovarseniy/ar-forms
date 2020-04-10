import psycopg2

SCHEMA_VERSION = '0.1'
SCHEMA_VERSION_PARAM = 'SCHEMA_VERSION'

DB_NAME = 'ar_forms'
DB_USER = 'ar_forms'
DB_PASS = 'master'


def _recreate_schema():
    conn, cur = get_cursor()

    cur.execute("DROP TABLE IF EXISTS paramters;")
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")

    cur.execute("CREATE TABLE parameters (name text PRIMARY KEY, value text);")
    cur.execute("INSERT INTO parameters (name, value) VALUES (%s, %s);", (SCHEMA_VERSION_PARAM, SCHEMA_VERSION))

    cur.execute("CREATE TABLE users ("
                "   id serial primary key,"
                "   login text not null unique,"
                "   display_name text not null,"
                "   password text"
                ");")

    conn.commit()
    del_cursor(conn, cur)


def _get_schema_version():
    conn, cur = get_cursor()

    try:
        cur.execute("SELECT value FROM parameters WHERE name = %s", (SCHEMA_VERSION_PARAM,))
        return cur.fetchone()[0]
    except psycopg2.ProgrammingError:
        return None
    finally:
        del_cursor(conn, cur)


def get_cursor():
    """Returns connection and cursor objects"""
    connection = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cursor = connection.cursor()
    return connection, cursor


def del_cursor(connection, cursor):
    """Closes connection and cursor"""
    cursor.close()
    connection.close()


_version = _get_schema_version()
if not _version:
    _recreate_schema()
elif _version != SCHEMA_VERSION:
    raise Exception("Wrong schema version")
