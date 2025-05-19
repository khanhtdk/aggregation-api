from app.controllers import TopProductsQuery
from tests import ControllerTest


class TopProductsQueryController(ControllerTest):
    def test_profile_1(self):
        """
        Test ProductTopFiveQuery controller: Profile #1 (no idexes).
        """
        self.time(TopProductsQuery(profile=1))

    def test_profile_2(self):
        """
        Test ProductTopFiveQuery controller: Profile #2 (indexed).
        """
        self.time(TopProductsQuery(profile=2))
