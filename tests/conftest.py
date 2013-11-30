# -*- coding: utf-8 -*-
"""
Directory-specific fixtures, hooks, etc. for py.test
"""
from clay import Clay
import pytest

from .helpers import TESTS


@pytest.fixture()
def c():
    return Clay(TESTS, {'foo': 'bar'})


@pytest.fixture()
def t(c):
    return c.get_test_client()
