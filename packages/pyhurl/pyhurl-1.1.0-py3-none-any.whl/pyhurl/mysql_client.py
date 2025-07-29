import pymysql
import pymysql.cursors
from dotenv import load_dotenv
import os


class MySQLClient:
    load_dotenv()
    __conn_properties = {
        'host': os.getenv('PYHURL_MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('PYHURL_MYSQL_PORT', 3306)),
        'database': os.getenv('PYHURL_MYSQL_DB'),
        'user': os.getenv('PYHURL_MYSQL_USER', 'root'),
        'password': os.getenv('PYHURL_MYSQL_PASSWORD'),
        'read_timeout': int(os.getenv('PYHURL_MYSQL_READ_TIMEOUT', 60)),
        'write_timeout': int(os.getenv('PYHURL_MYSQL_WRITE_TIMEOUT', 60)),
        'autocommit': bool(os.getenv('PYHURL_MYSQL_AUTO_COMMIT', False)),
        'cursorclass': pymysql.cursors.DictCursor,
    }

    @classmethod
    def get_connection(cls):
        return pymysql.connect(**cls.__conn_properties)

    @classmethod
    def close_connection(cls, conn):
        conn.close()

    @classmethod
    def execute(cls, sql, params=None, return_lastrowid=False):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cursor:
                ret = cursor.execute(sql, params)
                lastrowid = cursor.lastrowid
            conn.commit()
            return lastrowid if return_lastrowid else ret
        finally:
            cls.close_connection(conn)

    @classmethod
    def execute(cls, sql, params=None, return_lastrowid=False):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cursor:
                ret = cursor.execute(sql, params)
                lastrowid = cursor.lastrowid
            conn.commit()
            return lastrowid if return_lastrowid else ret
        finally:
            cls.close_connection(conn)

    @classmethod
    def update(cls, sql, params=None):
        return cls.execute(sql, params, return_lastrowid=False)

    @classmethod
    def insert(cls, sql, params=None):
        return cls.execute(sql, params, return_lastrowid=True)

    @classmethod
    def fetchone(cls, sql, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        finally:
            cls.close_connection(conn)

    @classmethod
    def fetchmany(cls, sql, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            cls.close_connection(conn)

    @classmethod
    def iterate(cls, sql, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                for row in cursor:
                    yield row
        finally:
            cls.close_connection(conn)
