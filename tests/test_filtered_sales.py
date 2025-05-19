from app.controllers import FilteredSalesQuery
from app.models import CURRENT_YEAR
from tests import ControllerTest


class FilteredSalesQueryController(ControllerTest):
    def setUp(self):
        super().setUp()

        # Init filter parameters
        self.params = {
            'product_name': 'Data Science Book',
            'region_name': 'Mid-Atlantic',
            'start_date': f'{CURRENT_YEAR}-02-01',
            'end_date': f'{CURRENT_YEAR}-03-01',
        }

    def test_profile_1(self):
        """
        Test FilteredSalesQuery controller: Profile #1 (no indexes).
        """
        self.time(FilteredSalesQuery(profile=1, **self.params))

    def test_profile_2(self):
        """
        Test FilteredSalesQuery controller: Profile #2 (indexed).
        """
        self.time(FilteredSalesQuery(profile=2, **self.params))

    def test_profile_3(self):
        """
        Test FilteredSalesQuery controller: Profile #3 (indexed, partitioning).
        """
        self.time(FilteredSalesQuery(profile=3, **self.params))
