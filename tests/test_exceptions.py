# -*- coding: utf-8 -*-
from __future__ import absolute_import

from clay.main import SOURCE_NOT_FOUND
from jinja2 import TemplateNotFound
from werkzeug.exceptions import HTTPException
import pytest
import socket

from .helpers import *


def setup_module():
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

 
def teardown_module():
    remove_test_dirs()


def test_friendly_notfound_of_templates(t):
    setup_module()

    create_file(get_source_path('foo.html'), u'foo{% include "bar.html" %}')

    resp = t.get('/hello.html')
    assert resp.status_code == HTTP_NOT_FOUND
    assert 'hello.html' in resp.data
    assert 'jinja2.exceptions' not in resp.data

    resp = t.get('/foo.html')
    assert resp.status_code == HTTP_NOT_FOUND
    assert 'bar.html' in resp.data
    print resp.data
    assert 'jinja2.exceptions' not in resp.data


def test_friendly_notfound_of_files(t):
    setup_module()

    resp = t.get('/foobar')
    assert resp.status_code == HTTP_NOT_FOUND
    assert 'foobar' in resp.data
    assert 'jinja2.exceptions' not in resp.data


def test_fail_if_source_dir_dont_exists(c):
    remove_test_dirs()

    def fake_run(**kwargs):
        return kwargs

    _run = c.app.run
    c.app.run = fake_run
    out = execute_and_read_stdout(c.run)

    c.app.run = _run
    make_dirs(SOURCE_DIR)

    assert SOURCE_NOT_FOUND in out


def test_make_dirs_wrong():
    with pytest.raises(OSError):
        make_dirs('/etc/bla')


def test_fix_settings():
    remove_test_dirs()
    bad_settings = dict(
        FILTER_PARTIALS = None,
        FILTER = None,
        INCLUDE = None,
        HOST = None,
        PORT = None,
    )
    c = Clay(TESTS, bad_settings)
    create_page('test.html', HTML)
    c.get_pages_index()

