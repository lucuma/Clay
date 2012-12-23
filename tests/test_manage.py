# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys

import clay
from clay.manage import main, manager
from flask import Flask

from .helpers import *


TEST_DIR = join(dirname(__file__), 'foobar')


def teardown_module():
    remove_dir(TEST_DIR)


def test_has_main():
    main()


def test_create_skeleton():
    make_dirs(TEST_DIR)
    sys.argv = [sys.argv[0], 'new', TEST_DIR]
    manager.run()
    assert os.path.isdir(join(TEST_DIR, 'source'))
    remove_dir(TEST_DIR)


def test_get_version():
    sys.argv = [sys.argv[0], 'version']
    o = execute_and_read_stdout(manager.run)
    assert o.strip() == clay.__version__


def test_can_run(c, monkeypatch):
    def fake_run(self, **config):
        assert config['use_debugger']
        assert not config['use_reloader']

    monkeypatch.setattr(Flask, 'run', fake_run)
    sys.argv = [sys.argv[0], 'run']
    manager.run()


def test_run_with_custom_host_and_port(c, monkeypatch):
    host = 'localhost'
    port = 9000
    def fake_run(self, **config):
        assert host == config['host']
        assert port == config['port']

    monkeypatch.setattr(Flask, 'run', fake_run)
    sys.argv = [sys.argv[0], 'run', dirname(__file__), str(host), str(port)]
    manager.run()


def test_can_build(c):
    make_dirs(TEST_DIR)
    make_dirs(TEST_DIR, 'source')
    sp = join(TEST_DIR, 'source', 'foo.txt')
    bp = join(TEST_DIR, 'build', 'foo.txt')
    create_file(sp, u'bar')

    sys.argv = [sys.argv[0], 'build', TEST_DIR]
    manager.run()
    assert os.path.exists(bp)

    remove_dir(TEST_DIR)


