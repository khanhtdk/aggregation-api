from tests import ApiTest


class ApiCaching(ApiTest):
    """Tests caching on all available endpoints."""

    def test_filter_sales(self):
        params = {'start_date': '2025-01-01', 'end_date': '2025-01-31'}
        self.describe_cache_time('/sales/', params=params)

    def test_monthly_sales(self):
        self.describe_cache_time('/sales/monthly-revenue/')

    def test_top_products(self):
        self.describe_cache_time('/sales/top-products/')
