# -*- coding: utf-8 -*-
import os
import shutil

from tests.helpers import *


def setup_module():
    try:
        shutil.rmtree(SOURCE_DIR)
    except OSError:
        pass
    try:
        shutil.rmtree(BUILD_DIR)
    except OSError:
        pass
    make_dirs(SOURCE_DIR)


def teardown_module():
    try:
        shutil.rmtree(SOURCE_DIR)
        shutil.rmtree(BUILD_DIR)
    except OSError:
        pass


def create_test_file(name):
    spath = get_source_path(name)
    bpath = get_build_path(name)
    create_file(spath, 'source')
    create_file(bpath, 'build')
    return spath, bpath


def test_build_dir_is_made(c):
    name = 'test.html'
    create_file(get_source_path(name), u'')
    try:
        shutil.rmtree(BUILD_DIR)
    except OSError:
        pass
    c.build_page(name)
    assert isdir(BUILD_DIR)


def test_make_dirs_wrong():
    with pytest.raises(OSError):
        make_dirs('/etc/bla')


def test_build_page(c):
    name = 'foo.html'
    create_file(get_source_path(name), u'foo{% include "bar.html" %}')
    create_file(get_source_path('bar.html'), u'bar')
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == 'foobar'


def test_build_file_without_process(c):
    name = 'main.css'
    content = "/* {% foobar %} */"
    create_file(get_source_path(name), content)
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == content.strip()


def test_do_not_copy_if_build_is_newer(c):
    name = 'test.txt'
    spath, bpath = create_test_file(name)
    t = os.path.getmtime(spath)
    os.utime(bpath, (-1, t + 1))
    c.build_page(name)
    assert read_content(bpath) == 'build'


def test_copy_if_source_is_newer(c):
    name = 'test.txt'
    spath, bpath = create_test_file(name)
    t = os.path.getmtime(bpath)
    os.utime(spath, (-1, t + 1))
    c.build_page(name)
    assert read_content(bpath) == 'source'


