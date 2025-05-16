from abc import ABC, abstractmethod
from typing import List

from . import app
from .utils import SQLite


class BaseQuery(ABC):
    def __init__(self, profile: int = 0):
        """
        :param profile:     Which profile is selected. Default is the first
                            profile starting from 0.
        """
        self.profile: int = profile
        self.db = SQLite(app.config['DATABASE_FILE'])

    @abstractmethod
    def available_profiles(self) -> List[str]:
        """
        Returns a list of query statements. Each query statement serves a
        performance profile and can be retrieved by its index.
        """

    def parse_results(self, results):
        return results

    @property
    def query(self) -> str:
        return self.available_profiles()[self.profile]

    def __call__(self):
        with self.db as conn:
            return self.parse_results(conn.fetchall(self.query))


class MonthlySalesQuery(BaseQuery):
    def parse_results(self, results):
        parse = lambda i: {'year': i[0], 'month': i[1], 'revenue': i[2]}
        return list(map(parse, results))

    def available_profiles(self) -> List[str]:
        return [
            # Query that uses the original Order model and leverages STRFTIME
            '''
                SELECT
                    STRFTIME('%Y', date_purchased) AS year,
                    STRFTIME('%m', date_purchased) AS month,
                    SUM(revenue)
                FROM orders
                GROUP BY year, month
                ORDER BY year, month
            ''',
        ]
