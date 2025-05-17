from app.controllers import FilteredSalesQuery
from tests import BaseTest


class FilteredSalesQueryController(BaseTest):
    def setUp(self):
        super().setUp()
        self.params = {
            'product_name': 'Data Science Book',
            'region_name': 'Mid-Atlantic',
            'start_date': '2024-01-01',
            'end_date': '2026-01-01',
        }

    def test_profile_1(self):
        """
        Test FilteredSalesQuery controller: Profile #1 (normalized, no indexes).
        """
        self.time(FilteredSalesQuery(profile=1, **self.params))
