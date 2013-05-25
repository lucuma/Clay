# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
from tempfile import mkdtemp

import clay
from clay.manage import main, manager
from flask import Flask

from .helpers import *


def test_has_main():
    main()


def test_create_skeleton():
    test_dir = mkdtemp()
    sys.argv = [sys.argv[0], 'new', test_dir]
    manager.run()
    assert os.path.isdir(join(test_dir, 'source'))
    remove_dir(test_dir)


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
    sys.argv = [sys.argv[0], 'run', mkdtemp(), str(host), str(port)]
    manager.run()


def test_can_build(c):
    test_dir = mkdtemp()
    make_dirs(test_dir, 'source')
    sp = join(test_dir, 'source', 'foo.txt')
    bp = join(test_dir, 'build', 'foo.txt')
    create_file(sp, u'bar')

    sys.argv = [sys.argv[0], 'build', '--path', test_dir]
    manager.run()
    assert os.path.exists(bp)
    remove_dir(test_dir)


def test_can_build_pattern(c):
    test_dir = mkdtemp()
    make_dirs(test_dir, 'source')
    sp1 = join(test_dir, 'source', 'foo.txt')
    bp1 = join(test_dir, 'build', 'foo.txt')
    create_file(sp1, u'bar')

    sp2 = join(test_dir, 'source', 'bar.txt')
    bp2 = join(test_dir, 'build', 'bar.txt')
    create_file(sp2, u'bar')

    sys.argv = [sys.argv[0], 'build', 'bar.txt', '--path', test_dir]
    manager.run()
    assert not os.path.exists(bp1)
    assert os.path.exists(bp2)
    assert read_content(bp2) == u'bar'
    remove_dir(test_dir)
