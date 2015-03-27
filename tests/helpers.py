# coding=utf-8
import io
import os
from os.path import dirname, join, isdir, exists
import shutil
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
from tempfile import mkdtemp

from clay.helpers import make_dirs, create_file


HTML = u'<!DOCTYPE html><html><head><title></title></head><body></body></html>'
HTTP_OK = 200
HTTP_NOT_FOUND = 404
TESTS = mkdtemp()
SOURCE_DIR = join(TESTS, 'source')
BUILD_DIR = join(TESTS, 'build')


def get_source_path(path):
    return join(SOURCE_DIR, path)


def get_build_path(path):
    return join(BUILD_DIR, path)


def create_page(name, content, encoding='utf8'):
    sp = get_source_path(name)
    make_dirs(dirname(sp))
    content = content.encode(encoding)
    create_file(sp, content, encoding=encoding)


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


def setup_function(f=None):
    make_dirs(SOURCE_DIR)
    make_dirs(BUILD_DIR)


def teardown_function(f=None):
    remove_dir(SOURCE_DIR)
    remove_dir(BUILD_DIR)
    remove_file(join(TESTS, 'settings.yml'))
