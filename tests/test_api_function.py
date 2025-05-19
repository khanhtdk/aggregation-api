from tests import ApiTest


class ApiFunctionality(ApiTest):
    """Tests functionality of all available endpoints."""

    def test_filter_sales(self):
        returned_items = self.get('/sales/', params={'start_date': '2025-01-01', 'end_date': '2025-01-31'})
        expected_items = list(filter(lambda i: '2025-01-' in i['sale_date'], returned_items))
        self.assertEqual(len(expected_items), len(returned_items))

    def test_monthly_sales(self):
        items = self.get('/sales/monthly-revenue/')
        self.assertGreater(len(items), 0)
        self.assertEqual(set(items[0].keys()), {'year', 'month', 'revenue'})

    def test_top_products(self):
        items = self.get('/sales/top-products/', params={'limit': 3})
        self.assertEqual(len(items), 3)
