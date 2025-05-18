import timeit
import unittest
from typing import Callable

from app import app


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.total_attempts = 200

    def tearDown(self):
        self.ctx.pop()

    def time(self, func: Callable):
        """
        Executes the input `func` and prints out its elapsed time in milliseconds.
        """
        elapsed = timeit.timeit(func, number=self.total_attempts) * 1000
        print(f'elapsed {elapsed:.2f}ms')
