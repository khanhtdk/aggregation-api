from abc import ABC, abstractmethod
from typing import List, Dict

from . import app
from .models import CURRENT_YEAR, BeforeCurrentYearSale, CurrentYearSale
from .utils import SQLite


class BaseQuery(ABC):
    def __init__(self, profile: int, **params):
        """
        :param profile:    Which profile is selected. Default is the first
                           profile starting from 0.
        :param params:     Custom parameters for populating the query.
        """
        # Validate profile
        if not isinstance(profile, int) or profile < 1:
            raise ValueError('Profile must be an integer >= 1')

        # Select query based on input profile
        try:
            self.query = self.query_profiles()[profile - 1]
            self.profile = profile
        except IndexError:
            raise ValueError(f'Profile {profile} does not exist')

        # Query population
        self.populate_query(**params)

        # Init SQLite wrapper as `db` instance
        self.db = SQLite(app.config['DATABASE_FILE'])

    @abstractmethod
    def query_profiles(self) -> List[str]:
        """
        Returns a list of query statements. Each query statement serves a
        performance profile and can be retrieved by its index.
        """

    def parse_results(self, results):
        """Parses the results of executed query into usable data."""
        return results

    def populate_query(self, **params):
        """Populates custom parameters into the query before it is used."""

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
        columns = ['year', 'month', 'revenue']
        return list(map(lambda res: dict(zip(columns, res)), results))

    def query_profiles(self) -> List[str]:
        strftime = lambda fmt: f'''STRFTIME('{fmt}', date)'''
        base_query = '''
            SELECT {year} AS selected_year, {month} AS selected_month, SUM(revenue)
            FROM sales
            GROUP BY selected_year, selected_month
            ORDER BY selected_year, selected_month;
        '''
        return [
            base_query.format(year=strftime('%Y'), month=strftime('%m')),  # profile 1
            base_query.format(year='year', month='month'),  # profile 2
            base_query.format(year='indexed_year', month='indexed_month'),  # profile 3
        ]


class FilteredSalesQuery(BaseQuery):
    """
    The controller that returns sales data matching a set of filters. It has 3
    profiles as follows:

        * Profile 1:    No use of indexes.

        * Profile 2:    Leverages indexing for joining fields and the date field.

        * Profile 3:    Leverages indexing like above plus partitioning tables.
    """

    def parse_results(self, results):
        columns = ['sale_date', 'product_name', 'revenue', 'region_name']
        return list(map(lambda res: dict(zip(columns, res)), results))

    def populate_query(self, product_name=None, region_name=None, start_date=None, end_date=None):
        # Initial conditions
        conditions = []

        def validate_date(d):
            """Validates date value."""
            if not SQLite.expects_date(d):
                raise ValueError(f'Value {d!r} is not a valid date')

        def range_condition(start=None, end=None) -> str:
            """Constructs range condition from start and/or end dates."""
            if start and end:
                return f'date BETWEEN {start!r} AND {end!r}'
            if start:
                return f'date >= {start!r}'
            if end:
                return f'date <= {end!r}'
            raise AssertionError('No input')

        def where_clause(start=None, end=None) -> str:
            """
            Constructs `WHERE` clause from list of preloaded conditions and
            optional inputs of start and end dates.
            """
            conds = conditions.copy()
            if start or end:
                conds.append(range_condition(start, end))
            if conds:
                cond = ' AND '.join(conds)
                return f'\nWHERE {cond}'
            return ''

        # Validate start date if set
        start_year_is_current = False
        if start_date:
            validate_date(start_date)
            start_year = start_date.split('-')[0]
            start_year_is_current = int(start_year) >= CURRENT_YEAR

        # Validate end date if set
        end_year_is_past = False
        if end_date:
            validate_date(end_date)
            end_year = end_date.split('-')[0]
            end_year_is_past = int(end_year) < CURRENT_YEAR

        # Ensure start date is before end date if both are set
        if start_date and end_date and start_date >= end_date:
            raise ValueError(f'`start_date` must be before `end_date`')

        # Insert condition for product name if set
        if product_name:
            conditions.append(f'product_name = {str(product_name)!r}')

        # Insert condition for region name if set
        if region_name:
            conditions.append(f'region_name = {str(region_name)!r}')

        # Match other profiles
        if self.profile != 3:
            # Append where clause to the query if conditions or date range is
            # not empty.
            self.query += where_clause(start_date, end_date)

        # Match profile 3
        ## Handles the case that only one partition (or table) gets involved
        elif start_year_is_current or end_year_is_past:
            table = (BeforeCurrentYearSale.__tablename__, CurrentYearSale.__tablename__)[start_year_is_current]
            self.query = self.query.format(table=table) + where_clause(start_date, end_date)

        ## Handles the case that both partitions (or tables) get involved
        else:
            # Constructs query that applies on first partition
            query_1 = self.query.format(table=BeforeCurrentYearSale.__tablename__)
            query_1 += where_clause(start=start_date)

            # Constructs query that applies on second partition
            query_2 = self.query.format(table=CurrentYearSale.__tablename__)
            query_2 += where_clause(end=end_date)

            # Final query is a UNION of both queries
            self.query = '\nUNION ALL\n'.join([query_1, query_2])

    def query_profiles(self) -> List[str]:
        return [
            # Profile 1: uses original `date`, `product_id`, and `region_id` fields
            '''
                SELECT s.date, p.name AS product_name, s.revenue, r.name AS region_name
                FROM sales s
                JOIN products p ON s.product_id = p.id
                JOIN regions r ON s.region_id = r.id
            ''',

            # Profile 2: uses indexed versions of `date`, `product_id`, and `region_id`
            '''
                SELECT s.indexed_date AS date, p.name AS product_name, s.revenue, r.name AS region_name
                FROM sales s
                JOIN products p ON s.indexed_product_id = p.id
                JOIN regions r ON s.indexed_region_id = r.id
            ''',

            # Profile 3: uses partitioned tables
            '''
                SELECT s.date, p.name AS product_name, s.revenue, r.name AS region_name
                FROM {table} s
                JOIN products p ON s.product_id = p.id
                JOIN regions r ON s.region_id = r.id
            ''',
        ]
