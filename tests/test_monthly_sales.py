from app.controllers import MonthlySalesQuery
from tests import BaseTest


class MonthlySalesQueryController(BaseTest):
    def test_profile_1(self):
        """
        Test MonthlySalesQuery controller: Profile #1 (strftime, no idexes).
        """
        self.time(MonthlySalesQuery(profile=1))

    def test_profile_2(self):
        """
        Test MonthlySalesQuery controller: Profile #2 (pre-populated fields).
        """
        self.time(MonthlySalesQuery(profile=2))

    def test_profile_3(self):
        """
        Test MonthlySalesQuery controller: Profile #3 (pre-populated fields + indexed).
        """
        self.time(MonthlySalesQuery(profile=3))
