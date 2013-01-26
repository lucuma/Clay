# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

from werkzeug.exceptions import HTTPException
import pytest
import socket

from clay.server import RequestLogger
from .helpers import *


def setup_module():
    remove_test_dirs()
    make_dirs(SOURCE_DIR)


def test_run_with_custom_host_and_port(c):
    class FakeServer(object):
        def __init__(self, hp, **kwargs):
            self.hp = hp

        def start(self):
            return self.hp

        def stop(self):
            pass

    def get_fake_server(host, port):
        return FakeServer((host, port))

    setup_module()
    _get_wsgi_server = c.server._get_wsgi_server
    c.server._get_wsgi_server = get_fake_server
    host = 'localhost'
    port = 9000
    h, p = c.run(host=host, port=port)
    c.server._get_wsgi_server = _get_wsgi_server
    assert host == h
    assert port == p


def test_run_port_is_already_in_use(c):
    ports = []

    class FakeServer(object):
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            raise socket.error()

        def stop(self):
            pass

    def get_fake_server(host, port):
        ports.append(port)
        return FakeServer()

    setup_module()
    _get_wsgi_server = c.server._get_wsgi_server
    c.server._get_wsgi_server = get_fake_server
    host = 'localhost'
    port = 9000
    c.run(host=host, port=port)
    c.server._get_wsgi_server = _get_wsgi_server

    expected = [p for p in range(port, port + 11)]
    assert ports == expected


def test_server_stop(c):
    log = []

    class FakeServer(object):
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            log.append('start')
            raise KeyboardInterrupt

        def stop(self):
            log.append('stop')

    def get_fake_server(host, port):
        return FakeServer()

    setup_module()
    _get_wsgi_server = c.server._get_wsgi_server
    c.server._get_wsgi_server = get_fake_server
    c.run()
    c.server._get_wsgi_server = _get_wsgi_server

    assert log == ['start', 'stop']
    

def test_run_with_invalid_port(c):
    with pytest.raises(Exception):
        c.run(port=-80)


def test_request_logger():
    def app(*args, **kwargs):
        pass

    l = RequestLogger(app)
    environ = {
        'REMOTE_ADDR': '192.168.0.25',
        'REQUEST_URI': '/lalala',
        'REQUEST_METHOD': 'HEAD',
    }
    now = datetime.now()
    out = execute_and_read_stdout(lambda: l.log_request(environ, now))
    expected = ' %s | 192.168.0.25  /lalala  (HEAD)\n' % now.strftime('%H:%M:%S')
    assert out == expected


def test_request_logger_as_middleware():
    called = []

    def app(*args, **kwargs):
        pass

    def start_response(*args, **kwargs):
        called.append(True)

    l = RequestLogger(app)
    l({}, start_response)
    assert not called


def test_request_logger_as_middleware_fail():
    called = []

    def app(*args, **kwargs):
        raise ValueError

    def start_response(*args, **kwargs):
        called.append(True)

    l = RequestLogger(app)
    with pytest.raises(ValueError):
        l({}, start_response)
    assert called


