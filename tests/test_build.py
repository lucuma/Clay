# -*- coding: utf-8 -*-
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


def test_build_file(c):
    name = 'main.css'
    content = """
    .icon1 { background-image: url('img/icon1.png'); }
    .icon2 { background-image: url('img/icon2.png'); }
    .icon3 { background-image: url('img/icon3.png'); }
    .icon4 { background-image: url('img/icon4.png'); }
    """
    create_file(get_source_path(name), content)
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == content.strip()


def test_build_page(c):
    name = 'foo.html'
    create_file(get_source_path(name), u'foo{% include "bar.html" %}')
    create_file(get_source_path('bar.html'), u'bar')
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == 'foobar'

