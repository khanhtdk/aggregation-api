from app.controllers import ProductTopFiveQuery
from tests import BaseTest


class ProductTopFiveQueryController(BaseTest):
    def test_profile_1(self):
        """
        Test ProductTopFiveQuery controller: Profile #1 (no idexes).
        """
        self.time(ProductTopFiveQuery(profile=1))
