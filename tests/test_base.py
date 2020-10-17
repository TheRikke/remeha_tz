import sys
from unittest import TestCase

import logging


class TestBase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if '-v' in sys.argv:
    level = logging.DEBUG
else:
    level = logging.CRITICAL
logging.basicConfig(stream=sys.stderr, level=level)
