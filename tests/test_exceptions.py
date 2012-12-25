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

    assert SOURCE_NOT_FOUND in out


def raise_socket_error_addrinuse():
    e = socket.error()
    e.errno = socket.errno.EADDRINUSE
    raise e


def test_run_port_is_already_in_use(c):
    setup_module()

    ports = []

    def fake_run(**kwargs):
        ports.append(kwargs['port'])
        raise_socket_error_addrinuse()

    _run = c.app.run
    c.app.run = fake_run

    port = 9000
    c.run(host='localhost', port=port)
    expected = [p for p in range(port, port + 11)]
    assert ports == expected

    c.app.run = _run


def test_run_invalid_port(c):
    out = execute_and_read_stdout(lambda: c.run(port=80))
    assert 'Permission denied' in out


def test_make_dirs_wrong():
    with pytest.raises(OSError):
        make_dirs('/etc/bla')


