import datetime
import sqlite3
from contextlib import closing
from typing import Optional, Tuple, List, Any


class SQLite:
    """Simple wrapper for handling direct connection to SQLite."""

    @staticmethod
    def expects_date(value: str) -> bool:
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False

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
