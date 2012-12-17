# -*- coding: utf-8 -*-
import io
from os.path import dirname, join, isdir
import pytest

from clay import Clay
from clay.helpers import make_dirs, create_file


HTTP_OK = 200
HTTP_NOT_FOUND = 404
SOURCE_DIR = join(dirname(__file__), 'source')
BUILD_DIR = join(dirname(__file__), 'build')


@pytest.fixture(scope="module")
def c():
    root = dirname(__file__)
    return Clay(root)


@pytest.fixture(scope="module")
def t(c):
    return c.get_test_client()


def get_source_path(path):
    return join(SOURCE_DIR, path)


def get_build_path(path):
    return join(BUILD_DIR, path)


def read_content(path, encoding='utf8'):
    with io.open(path, 'r', encoding=encoding) as f:
        return f.read().encode(encoding)

