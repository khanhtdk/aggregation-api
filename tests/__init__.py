import json
import timeit
import unittest
from functools import partial
from typing import Callable
from urllib.parse import urlencode

from app import app


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()


class ControllerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.total_attempts = 200

    def time(self, func: Callable):
        """
        Executes the input `func` and prints out its elapsed time in milliseconds.
        """
        elapsed = timeit.timeit(func, number=self.total_attempts) * 1000
        print(f'elapsed {elapsed:.2f}ms')


class ApiTest(BaseTest):
    def setUp(self):
        # Set secret key used for testing
        app.config['API_SECRET_KEY'] = 'testing'
        # Init from super class
        super().setUp()
        # Init app client
        self.client = app.test_client()
        self.client.testing = True

    def get(self, endpoint, headers=None, params=None):
        """Sends an authenticated GET request to app endpoints."""
        headers = headers or {}
        # Insert auth header
        headers['X-Api-Key'] = 'testing'
        # Embed query params to request endpoint
        if params:
            endpoint += '?' + urlencode(params)
        # Proceeds to request
        response = self.client.get(endpoint, headers=headers)
        # Ensures request has succeeded
        self.assertTrue(200 <= response.status_code < 300)
        # Parses and returns response in JSON
        return json.loads(response.get_data(as_text=True))

    def time_get(self, endpoint, params=None, headers=None):
        """Returns elapsed time in milliseconds for a GET request."""
        request = partial(self.get, endpoint, params=params, headers=headers)
        elapsed = timeit.timeit(request, number=1) * 1000
        return elapsed

    def describe_cache_time(self, endpoint, params=None, headers=None):
        """
        Tests cache efficiency and shows elapsed time for both before and after
        caching requests.
        """
        # Insert cache param
        params = params or {}
        params['cache'] = 1
        # Time first and second requests
        e1, e2 = [self.time_get(endpoint, headers=headers, params=params) for _ in range(2)]
        # Ensures second request takes less time than the first one
        self.assertLess(e2, e1)
        # Prints output
        print('before:', f'{e1:.2f}ms', '|', 'after:', f'{e2:.2f}ms')
