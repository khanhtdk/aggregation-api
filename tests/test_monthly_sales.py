from app.controllers import MonthlySalesQuery
from tests import BaseTest


class MonthlySalesQueryController(BaseTest):
    def test_profile_1(self):
        """
        Test MonthlySalesQuery controller: Profile #1 (use unoptimized query).
        """
        self.time(MonthlySalesQuery(profile=1))

    def test_profile_2(self):
        """
        Test MonthlySalesQuery controller: Profile #2 (use split date query).
        """
        self.time(MonthlySalesQuery(profile=2))

    def test_profile_3(self):
        """
        Test MonthlySalesQuery controller: Profile #3 (use split date query with
        composite index).
        """
        self.time(MonthlySalesQuery(profile=3))
