import datetime
import sqlite3
from contextlib import closing
from functools import wraps
from typing import Optional, Tuple, List, Any, Callable

from flask import request, abort


class SQLite:
    """Simple wrapper for handling direct connection to SQLite."""

    @staticmethod
    def validates_date(value: str) -> str:
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
            return value
        except (ValueError, TypeError):
            raise ValueError(f'Value {value!r} is not a valid date string')

    def __init__(self, db_file: str):
        self.db_file: str = db_file
        self._conn: Optional[sqlite3.Connection] = None

    def fetchall(self, sql: str, *args, **kwargs) -> List[Tuple[Any, ...]]:
        """
        Executes the input SQL statement and returns all rows fetched from the resultset.
        """
        assert self._conn is not None, 'No connection'
        with closing(self._conn.cursor()) as cursor:
            cursor.execute(sql, *args, **kwargs)
            return cursor.fetchall()

    def __enter__(self):
        self._conn = sqlite3.connect(self.db_file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
        self._conn = None


class SimpleAuthByHeader:
    """
    A simple class for authenticating a request that reads value from the
    pre-defined header, matches the found value against its configured secret
    key, and returns `True` if both values are matched, otherwise it returns
    `False`.
    """

    def __init__(self, header_name: str, secret_key: str | Callable):
        """
        :param header_name:    Request header that contains a secret key.
        :param secret_key:     Secret key used for authentication. A callable
                               is accepted for lazy loading.
        """
        self.header_name = header_name
        self._secret_key = secret_key

    @property
    def secret_key(self):
        if callable(self._secret_key):
            self._secret_key = self._secret_key()
        return self._secret_key

    def protects(self, func):
        """Enables authentication functionality for wrapped methods."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Reads secret key from request header
            secret_key = request.headers.get(self.header_name)
            # Ensures secret key from request header is set
            if not secret_key:
                abort(401, 'Authentication required')
            # Checks if the request secret key matches the configured secret key
            if secret_key != self.secret_key:
                abort(401, 'Invalid secret key')
            # Successfully authenticated
            return func(*args, **kwargs)
        return wrapper


def getbool(value) -> bool:
    """Returns a boolean if value is bool-alike."""
    value = str(value).lower()
    if value in ('1', 'true', 'on'): return True
    if value in ('0', 'false', 'off'): return False
    raise ValueError(f'Value {value!r} is not a valid boolean value')
