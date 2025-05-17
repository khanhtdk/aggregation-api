from abc import ABC, abstractmethod
from typing import List, Dict

from . import app
from .utils import SQLite


class BaseQuery(ABC):
    def __init__(self, profile: int):
        """
        :param profile:     Which profile is selected. Default is the first
                            profile starting from 0.
        """
        # Validate profile
        if not isinstance(profile, int) or profile < 1:
            raise ValueError('Profile must be an integer >= 1')

        # Select query based on input profile
        try:
            self.query = self.available_queries()[profile - 1]
        except IndexError:
            raise ValueError(f'Profile {profile} does not exist')

        # Init SQLite wrapper as `db` instance
        self.db = SQLite(app.config['DATABASE_FILE'])

    @abstractmethod
    def available_queries(self) -> List[str]:
        """
        Returns a list of query statements. Each query statement serves a
        performance profile and can be retrieved by its index.
        """

    def parse_results(self, results):
        """Parses the results of executed query into usable data."""
        return results

    def __call__(self):
        """Executes the selected profile's query and returns parsed results."""
        with self.db as conn:
            return self.parse_results(conn.fetchall(self.query))


class MonthlySalesQuery(BaseQuery):
    """
    The controller used for querying monthly sales data. It has 3 available
    profiles as follows:

        * Profile 1:    Query that extracts `year` and `month` from `date` field
                        using STRFTIME().

        * Profile 2:    Query that directly uses pre-populated `year` and `month`
                        fields.

        * Profile 3:    Query that uses pre-populated `indexed_year` and `indexed_month`
                        fields with composite index enabled.
    """

    def parse_results(self, results) -> List[Dict[str, str | float]]:
        parse = lambda i: {'year': i[0], 'month': i[1], 'revenue': i[2]}
        return list(map(parse, results))

    def available_queries(self) -> List[str]:
        strftime = lambda fmt: f'''STRFTIME('{fmt}', date)'''
        base_query = '''
            SELECT {year} AS selected_year, {month} AS selected_month, SUM(revenue)
            FROM orders
            GROUP BY selected_year, selected_month
            ORDER BY selected_year, selected_month;
        '''
        return [
            base_query.format(year=strftime('%Y'), month=strftime('%m')),  # profile 1
            base_query.format(year='year', month='month'),  # profile 2
            base_query.format(year='indexed_year', month='indexed_month'),  # profile 3
        ]
