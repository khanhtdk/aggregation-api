from flask import Flask

# Init app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')

# Load views
from .views import FilteredSalesApiView, MonthlySalesApiView, TopProductsApiView

# Register endpoints
app.add_url_rule('/sales/', view_func=FilteredSalesApiView.as_view('filter-sales'))
app.add_url_rule('/sales/monthly-revenue/', view_func=MonthlySalesApiView.as_view('monthly-revenue'))
app.add_url_rule('/sales/top-products/', view_func=TopProductsApiView.as_view('top-products'))
