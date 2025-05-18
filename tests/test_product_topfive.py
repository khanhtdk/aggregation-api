from app.controllers import ProductTopFiveQuery
from tests import BaseTest


class ProductTopFiveQueryController(BaseTest):
    def test_profile_1(self):
        """
        Test ProductTopFiveQuery controller: Profile #1 (no idexes).
        """
        self.time(ProductTopFiveQuery(profile=1))

    def test_profile_2(self):
        """
        Test ProductTopFiveQuery controller: Profile #2 (indexed).
        """
        self.time(ProductTopFiveQuery(profile=2))
