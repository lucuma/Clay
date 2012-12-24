# -*- coding: utf-8 -*-
from __future__ import absolute_import

from clay.main import SOURCE_NOT_FOUND_HELP
from jinja2 import TemplateNotFound
from werkzeug.exceptions import HTTPException
import pytest

from .helpers import *


def setup_module():
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

 
def teardown_module():
    remove_test_dirs()


def test_notfound(t):
    remove_test_dirs()
    with pytest.raises(TemplateNotFound):
        t.get('/lalalala.html')


def test_notfound_file(t):
    remove_test_dirs()
    resp = t.get('/favicon.io')
    assert resp.status_code == HTTP_NOT_FOUND


def test_fail_if_source_dir_dont_exists(c):
    remove_test_dirs()

    def fake_run(**kwargs):
        return kwargs

    _run = c.app.run
    c.app.run = fake_run
    out = execute_and_read_stdout(c.run)

    c.app.run = _run
    make_dirs(SOURCE_DIR)

    assert SOURCE_NOT_FOUND_HELP in out


def test_make_dirs_wrong():
    with pytest.raises(OSError):
        make_dirs('/etc/bla')


