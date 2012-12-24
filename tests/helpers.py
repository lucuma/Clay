# -*- coding: utf-8 -*-
import io
import os
from os.path import dirname, join, isdir, realpath, exists
import shutil
from StringIO import StringIO
import sys

import pytest

from clay import Clay
from clay.helpers import make_dirs, create_file


HTML = u'<!DOCTYPE html><html><head><title></title></head><body></body></html>'

HTTP_OK = 200
HTTP_NOT_FOUND = 404
TESTS = dirname(__file__)
SOURCE_DIR = join(TESTS, 'source')
BUILD_DIR = join(TESTS, 'build')


@pytest.fixture(scope="module")
def c():
    return Clay(TESTS)


@pytest.fixture(scope="module")
def t(c):
    return c.get_test_client()


def remove_test_dirs():
    remove_dir(SOURCE_DIR)
    remove_dir(BUILD_DIR)


def get_source_path(path):
    return join(SOURCE_DIR, path)


def get_build_path(path):
    return join(BUILD_DIR, path)


def read_content(path, encoding='utf8'):
    with io.open(path, 'r', encoding=encoding) as f:
        return f.read().encode(encoding)


def remove_file(path):
    if exists(path):
        os.remove(path)


def remove_dir(path):
    if isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def execute_and_read_stdout(f):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    f()
    sys.stdout = old_stdout
    mystdout.seek(0)
    return mystdout.read()

