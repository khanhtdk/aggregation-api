from app.controllers import MonthlySalesQuery
from tests import BaseTest


class MonthlySalesTestCase(BaseTest):
    def test_original_query(self):
        """
        Query that uses the first profile of the controller which applies to the
        original Order model.
        """
        self.time(MonthlySalesQuery())

    def test_split_date_query(self):
        """
        Query that uses the second profile of the controller which applies to the
        optimized SplitDateOrder model.
        """
        self.time(MonthlySalesQuery(1))
