# -*- coding: utf-8 -*-
import os
import shutil

from tests.helpers import *


def teardown_module():
    remove_test_dirs()


def get_file_paths(name):
    sp = get_source_path(name)
    bp = get_build_path(name)
    return sp, bp


def create_test_file(name):
    make_dirs(BUILD_DIR)
    sp, bp = get_file_paths(name)
    create_file(sp, 'source')
    create_file(bp, 'build')
    return sp, bp


def test_make_dirs_wrong():
    with pytest.raises(OSError):
        make_dirs('/etc/bla')


def test_build_dir_is_made(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'test.html'
    sp, bp = get_file_paths(name)
    create_file(sp, u'')
    c.build_page(name)
    assert isdir(BUILD_DIR)


def test_build_page(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'foo.html'
    sp1, bp1 = get_file_paths(name)
    sp2, bp2 = get_file_paths('bar.html')

    create_file(sp1, u'foo{% include "bar.html" %}')
    create_file(sp2, u'bar')
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == 'foobar'


def test_build_file_without_process(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'main.css'
    sp, bp = get_file_paths(name)
    content = "/* {% foobar %} */"
    create_file(sp, content)
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == content.strip()


def test_do_not_copy_if_build_is_newer(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'test.txt'
    sp, bp = create_test_file(name)
    t = os.path.getmtime(sp)
    os.utime(bp, (-1, t + 1))
    c.build_page(name)
    assert read_content(bp) == 'build'


def test_copy_if_source_is_newer(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'test.txt'
    sp, bp = create_test_file(name)
    t = os.path.getmtime(bp)
    os.utime(sp, (-1, t + 1))
    c.build_page(name)
    assert read_content(bp) == 'source'


def test_rename_tmpl_file(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'test.txt.tmpl'
    sp, bp = get_file_paths(name)
    create_file(sp, u'lalala')
    bpreal = get_build_path('test.txt')

    c.build_page(name)
    assert os.path.exists(bpreal)
    assert not os.path.exists(bp)


def test_settings_as_template_build_context():
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    c = Clay(TESTS, {'who': u'world'})
    t = c.get_test_client()

    name = 'test.txt.tmpl'
    sp = get_source_path(name)
    bp = get_build_path('test.txt')
    create_file(sp, u'Hello {{ who }}!')
    
    c.build_page(name)
    assert read_content(bp) == u'Hello world!'


def test_build_all(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR, 'sub')

    sp1, bp1 = get_file_paths('a.txt')
    sp2 = get_source_path('b.txt.tmpl')
    bp2 = get_build_path('b.txt')
    sp3, bp3 = get_file_paths('sub/c.txt')

    create_file(sp1, u'foo')
    create_file(sp2, u'bar')
    create_file(sp3, u'mwahaha')

    c.build()
    assert os.path.exists(bp1)
    assert os.path.exists(bp2)
    assert os.path.exists(bp3)


def test_translate_absolute_to_relative(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR, 'foo')

    sp1, bp1 = get_file_paths('wtf.html')
    sp2, bp2 = get_file_paths('foo/wtf.html')
    content = u"""<!DOCTYPE html><html><head><title>%s</title><link href="/styles/test.css"></head><body></body></html>"""
    create_file(sp1, content % 'wtf')
    create_file(sp2, content % 'foo/wtf')

    c.build()

    c1 = read_content(bp1)
    assert '<link href="styles/test.css">' in c1
    c2 = read_content(bp2)
    assert '<link href="../styles/test.css"' in c2


def test_translate_absolute_to_relative_index(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR, 'bar')

    sp1, bp1 = get_file_paths('index.html')
    sp2, bp2 = get_file_paths('bar/index.html')
    content = u"""<!DOCTYPE html><html><head><title>%s</title></head><body><a href="/">Home</a></body></html>"""
    create_file(sp1, content % 'index')
    create_file(sp2, content % 'bar/index')

    c.build()

    c1 = read_content(bp1)
    assert '<a href="index.html">Home</a>' in c1
    c2 = read_content(bp2)
    assert '<a href="../index.html">Home</a>' in c2


def test_ignore_external_urls(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    sp1, bp1 = get_file_paths('t1.html')
    sp2, bp2 = get_file_paths('t2.html')
    sp3, bp3 = get_file_paths('t3.html')
    c1 = u"""<!DOCTYPE html><html><head><title></title></head><body><a href="//google.com"></a></body></html>"""
    c2 = u"""<!DOCTYPE html><html><head><title></title></head><body><a href="http://example.net/foo/bar"></a></body></html>"""
    c3 = u"""<!DOCTYPE html><html><head><title></title></head><body><a href="mailto:bob@example.com"></a></body></html>"""
    create_file(sp1, c1)
    create_file(sp2, c2)
    create_file(sp3, c3)

    c.build()
    assert read_content(bp1) == c1
    assert read_content(bp2) == c2
    assert read_content(bp3) == c3


def test_setting_filter_fragments(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    sp1, bp1 = get_file_paths('a.html')
    sp2, bp2 = get_file_paths('b.html')
    c1 = u"""<!DOCTYPE html><html><head><title></title></head><body></body></html>"""
    c2 = u"lalala"
    create_file(sp1, c1)
    create_file(sp2, c2)

    c.settings['FILTER_PARTIALS'] = True
    c.build()
    assert exists(bp1)
    assert not exists(bp2)

    c.settings['FILTER_PARTIALS'] = False
    c.build()
    assert exists(bp1)
    assert exists(bp2)


def test_setting_force_fragment_inclusion(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'fragment.html'
    sp, bp = get_file_paths(name)
    create_file(sp, u"lalala")

    c.settings['FILTER_PARTIALS'] = True
    c.settings['VIEWS_INCLUDE'] = [name,]
    c.build()
    assert exists(bp)


def test_setting_force_ignore(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR)

    name = 'fullpage.html'
    sp, bp = get_file_paths(name)
    content = u"""<!DOCTYPE html><html><head><title></title></head><body></body></html>"""
    create_file(sp, content)

    c.settings['VIEWS_IGNORE'] = [name,]
    c.build()
    assert not exists(bp)


