from app.controllers import FilteredSalesQuery
from tests import BaseTest


class FilteredSalesQueryController(BaseTest):
    def setUp(self):
        super().setUp()

        # Init filter parameters
        self.params = {
            'product_name': 'Data Science Book',
            'region_name': 'Mid-Atlantic',
            'start_date': '2024-01-01',
            'end_date': '2025-01-01',
        }

    def test_profile_1(self):
        """
        Test FilteredSalesQuery controller: Profile #1 (normalized, no indexes).
        """
        self.time(FilteredSalesQuery(profile=1, **self.params))

    def test_profile_2(self):
        """
        Test FilteredSalesQuery controller: Profile #2 (normalized, indexed).
        """
        self.time(FilteredSalesQuery(profile=2, **self.params))
