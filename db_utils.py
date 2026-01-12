import os
import threading
import mysql.connector
from mysql.connector import pooling
from flask import g, has_app_context
from werkzeug.local import LocalProxy

RETRYABLE_ERRORS = {2006, 2013, 2055}

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name=os.getenv("MYSQL_POOL_NAME", "neighbourly_pool"),
            pool_size=int(os.getenv("MYSQL_POOL_SIZE", 5)),
            pool_reset_session=True,
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            passwd=os.getenv("MYSQL_PASSWORD", "Helloworld1$"),
            database=os.getenv("MYSQL_DATABASE", "Neighbourly_Database"),
            ssl_disabled=True,
        )
    return _pool


def get_db_connection():
    if has_app_context():
        if "db_conn" not in g:
            g.db_conn = _get_pool().get_connection()
        return g.db_conn, False
    return _get_pool().get_connection(), True


def reset_db_connection():
    if has_app_context():
        conn = g.pop("db_conn", None)
        if conn is not None:
            conn.close()


def init_app(app):
    @app.teardown_appcontext
    def close_connection(exception=None):
        conn = g.pop("db_conn", None)
        if conn is not None:
            conn.close()


class CursorProxy:
    def __init__(self):
        self._cursor = None
        self._conn = None
        self._close_connection_after = False
        self._lastrowid = None

    def _ensure_cursor(self):
        if self._cursor is not None:
            return
        self._conn, self._close_connection_after = get_db_connection()
        self._cursor = self._conn.cursor()

    def _cleanup(self):
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None
        if self._close_connection_after and self._conn is not None:
            self._conn.close()
        self._conn = None
        self._close_connection_after = False

    def execute(self, *args, **kwargs):
        self._cleanup()
        for attempt in range(2):
            self._ensure_cursor()
            try:
                result = self._cursor.execute(*args, **kwargs)
                self._lastrowid = self._cursor.lastrowid
                return result
            except mysql.connector.Error as err:
                self._cleanup()
                if err.errno in RETRYABLE_ERRORS and attempt == 0:
                    reset_db_connection()
                    continue
                raise

    def executemany(self, *args, **kwargs):
        self._cleanup()
        for attempt in range(2):
            self._ensure_cursor()
            try:
                result = self._cursor.executemany(*args, **kwargs)
                self._lastrowid = self._cursor.lastrowid
                return result
            except mysql.connector.Error as err:
                self._cleanup()
                if err.errno in RETRYABLE_ERRORS and attempt == 0:
                    reset_db_connection()
                    continue
                raise

    def fetchone(self):
        if self._cursor is None:
            return None
        try:
            return self._cursor.fetchone()
        finally:
            self._cleanup()

    def fetchall(self):
        if self._cursor is None:
            return []
        try:
            return self._cursor.fetchall()
        finally:
            self._cleanup()

    @property
    def lastrowid(self):
        return self._lastrowid


class DBProxy:
    def __init__(self, cursor_proxy):
        self._cursor_proxy = cursor_proxy

    def _get_connection(self):
        if self._cursor_proxy._conn is not None:
            return self._cursor_proxy._conn, self._cursor_proxy._close_connection_after, True
        conn, close_after = get_db_connection()
        return conn, close_after, False

    def commit(self):
        for attempt in range(2):
            conn, close_after, from_cursor = self._get_connection()
            try:
                conn.commit()
                return
            except mysql.connector.Error as err:
                if err.errno in RETRYABLE_ERRORS and attempt == 0:
                    if close_after:
                        conn.close()
                    reset_db_connection()
                    continue
                raise
            finally:
                self._cursor_proxy._cleanup()
                if close_after and not from_cursor:
                    conn.close()

    def rollback(self):
        conn, close_after, from_cursor = self._get_connection()
        try:
            conn.rollback()
        finally:
            self._cursor_proxy._cleanup()
            if close_after and not from_cursor:
                conn.close()

    def close(self):
        if has_app_context():
            reset_db_connection()
        else:
            conn, close_after, from_cursor = self._get_connection()
            if close_after and not from_cursor:
                conn.close()


_thread_state = threading.local()


def _get_cursor_proxy():
    if has_app_context():
        if "cursor_proxy" not in g:
            g.cursor_proxy = CursorProxy()
        return g.cursor_proxy
    if not hasattr(_thread_state, "cursor_proxy"):
        _thread_state.cursor_proxy = CursorProxy()
    return _thread_state.cursor_proxy


def _get_db_proxy():
    cursor_proxy = _get_cursor_proxy()
    if not hasattr(cursor_proxy, "_db_proxy"):
        cursor_proxy._db_proxy = DBProxy(cursor_proxy)
    return cursor_proxy._db_proxy


db = LocalProxy(_get_db_proxy)
mycursor = LocalProxy(_get_cursor_proxy)
