from typing import ClassVar, Type, Callable, Optional, List, Tuple

from flask import jsonify, request
from flask.views import MethodView

from . import app
from .controllers import BaseQueryController, FilteredSalesQuery, MonthlySalesQuery, TopProductsQuery, ParamError
from .utils import SimpleAuthByHeader, SQLite, getbool

# Init auth instance
auth = SimpleAuthByHeader(
    header_name='X-Api-Key',
    secret_key=lambda: app.config['API_SECRET_KEY'],
)


class QueryApiView(MethodView):
    """
    An abstract view that accepts GET requests, reads parameters from URL query
    string, and executes the pre-defined controller to acquire and return results.
    """

    # Enforces authentication for accessing to all methods
    decorators = [auth.protects]

    # Controller class used as handler for this view
    query_class: ClassVar[Type[BaseQueryController]] = None

    # Define additional query parameters that are parsed from URL query string
    # and accepted to process by the controller.
    query_params: ClassVar[Optional[List[Tuple[str, Optional[Callable]]]]] = None

    def get_query_params(self):
        """Reads query parameters from URL query string."""

        # Implicit parameters expected by BaseQueryController
        param_defs = [('profile', int), ('cache', getbool)]
        # Merge with pre-defined custom parameters
        param_defs += self.query_params or []
        # Reads parameters from query string
        params = {}
        for name, type_ in dict(param_defs).items():
            value = request.args.get(name)
            if value is not None:
                if type_ is not None:
                    try:
                        value = type_(value)
                    except (TypeError, ValueError):
                        raise ParamError(f'Invalid argument "{name}={value}"')
                params[name] = value
        return params

    def get(self):
        """Listens to GET requests."""

        # Ensure query class is properly configured
        if not self.query_class:
            raise TypeError('No query_class configured')
        try:
            # Read query params
            params = self.get_query_params()
            # Init query instance with expected query params
            query_instance = self.query_class(**params)
            # Execute query instance and return response
            return jsonify(query_instance())
        except ParamError as e:
            # Response if invalid parameters encountered
            return jsonify({'error': str(e)}, 400)


class FilteredSalesApiView(QueryApiView):
    """Lists sales with set of filters."""

    query_class = FilteredSalesQuery
    query_params = [
        ('product_name', str),
        ('region_name', str),
        ('start_date', SQLite.validates_date),
        ('end_date', SQLite.validates_date),
    ]


class MonthlySalesApiView(QueryApiView):
    """Serves monthly sales queries."""

    query_class = MonthlySalesQuery


class TopProductsApiView(QueryApiView):
    """Serves top products queries."""

    query_class = TopProductsQuery
    query_params = [('limit', int)]
