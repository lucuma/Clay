# coding=utf-8
"""
Directory-specific fixtures, hooks, etc. for py.test
"""
import shutil

from clay import Clay
import pytest

from .helpers import TESTS, SOURCE_DIR, BUILD_DIR


def setup_function(function):
    """ Invoked for every test function in the module.
    """
    pass


def teardown_function(function):
    """ Invoked for every test function in the module.
    """
    try:
        shutil.rmtree(SOURCE_DIR)
    except OSError:
        pass
    try:
        shutil.rmtree(BUILD_DIR)
    except OSError:
        pass


@pytest.fixture()
def c():
    return Clay(TESTS, {'foo': 'bar'})


@pytest.fixture()
def t(c):
    return c.get_test_client()
