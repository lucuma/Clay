# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import shutil

from .helpers import *


def setup_module():
    remove_test_dirs()
    make_dirs(SOURCE_DIR)
    make_dirs(BUILD_DIR)


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


def test_build_dir_is_made(c):
    setup_module()

    name = 'test.html'
    sp, bp = get_file_paths(name)
    create_file(sp, u'')
    c.build_page(name)
    assert isdir(BUILD_DIR)


def test_build_page(c):
    setup_module()
    c.settings['FILTER_PARTIALS'] = False

    name = 'foo.html'
    sp1, bp1 = get_file_paths(name)
    sp2, bp2 = get_file_paths('bar.html')

    create_file(sp1, u'foo{% include "bar.html" %}')
    create_file(sp2, u'bar')
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == 'foobar'


def test_build_file_without_process(c):
    setup_module()

    name = 'main.css'
    sp, bp = get_file_paths(name)
    content = "/* {% foobar %} */"
    create_file(sp, content)
    c.build_page(name)
    result = read_content(get_build_path(name))
    assert result.strip() == content.strip()


def test_do_not_copy_if_build_is_newer(c):
    setup_module()

    name = 'test.txt'
    sp, bp = create_test_file(name)
    t = os.path.getmtime(sp)
    os.utime(bp, (-1, t + 1))
    c.build_page(name)
    assert read_content(bp) == 'build'


def test_copy_if_source_is_newer(c):
    setup_module()

    name = 'test.txt'
    sp, bp = create_test_file(name)
    t = os.path.getmtime(bp)
    os.utime(sp, (-1, t + 1))
    c.build_page(name)
    assert read_content(bp) == 'source'


def test_rename_tmpl_file(c):
    c.settings['FILTER_PARTIALS'] = False
    setup_module()

    name = 'test.txt.tmpl'
    sp, bp = get_file_paths(name)
    create_file(sp, u'lalala')
    bpreal = get_build_path('test.txt')

    c.build_page(name)
    assert os.path.exists(bpreal)
    assert not os.path.exists(bp)


def test_settings_as_template_build_context():
    setup_module()

    c = Clay(TESTS, {'who': u'world', 'FILTER_PARTIALS': False})
    t = c.get_test_client()

    name = 'test.txt.tmpl'
    sp = get_source_path(name)
    bp = get_build_path('test.txt')
    create_file(sp, u'Hello {{ who }}!')
    
    c.build_page(name)
    assert read_content(bp) == u'Hello world!'


def test_build_all(c):
    c.settings['FILTER_PARTIALS'] = False
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
    content = u"""<!DOCTYPE html><html><head><title>%s</title>
    <link href="/styles/reset.css">
    <link href="/styles/test.css">
    <script src="/scripts/main.js"></script>
    <img src="/static/img.jpg" data-src="/static/imgBig.jpg">
    </head><body></body></html>"""
    create_file(sp1, content % 'wtf')
    create_file(sp2, content % 'foo/wtf')

    c.build()

    page = read_content(bp1)
    assert '<link href="styles/reset.css">' in page
    assert '<link href="styles/test.css">' in page
    assert '<script src="scripts/main.js">' in page
    assert '<img src="static/img.jpg" data-src="static/imgBig.jpg">' in page
    page = read_content(bp2)
    assert '<link href="../styles/reset.css">' in page
    assert '<link href="../styles/test.css">' in page
    assert '<script src="../scripts/main.js">' in page
    assert '<img src="../static/img.jpg" data-src="../static/imgBig.jpg">' in page


def test_translate_absolute_to_relative_index(c):
    remove_test_dirs()
    make_dirs(SOURCE_DIR, 'bar')

    sp1, bp1 = get_file_paths('index.html')
    sp2, bp2 = get_file_paths('bar/index.html')
    content = u"""<!DOCTYPE html><html><head><title>%s</title></head>
    <body><a href="/">Home</a></body></html>"""
    create_file(sp1, content % 'index')
    create_file(sp2, content % 'bar/index')

    c.build()

    page = read_content(bp1)
    assert '<a href="index.html">Home</a>' in page
    page = read_content(bp2)
    assert '<a href="../index.html">Home</a>' in page


def test_translate_ignore_external_urls(c):
    setup_module()

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


def test_filter_hidden_files(c):
    setup_module()

    sp, bp = get_file_paths('.DS_Store')
    create_file(sp, u'lorem ipsum')
    c.build()
    assert not exists(bp)


def test_setting_filter_fragments(c):
    setup_module()

    sp, bp = get_file_paths('fragment.html')
    create_file(sp, u"lalala")

    c.settings['FILTER_PARTIALS'] = True
    c.build()
    assert not exists(bp)

    c.settings['FILTER_PARTIALS'] = False
    c.build()
    assert exists(bp)


def test_setting_force_fragment_inclusion(c):
    setup_module()

    name = 'fragment.html'
    sp, bp = get_file_paths(name)
    create_file(sp, u"lalala")

    c.settings['FILTER_PARTIALS'] = True
    c.settings['INCLUDE'] = [name,]
    c.build()
    assert exists(bp)


def test_setting_force_ignore(c):
    setup_module()

    name = 'fullpage.html'
    sp, bp = get_file_paths(name)
    content = HTML
    create_file(sp, content)

    c.settings['FILTER'] = [name,]
    c.build()
    assert not exists(bp)


def test_build__index(c):
    setup_module()
    make_dirs(SOURCE_DIR, 'bbb')

    sp1, bp1 = get_file_paths('aaa.html')
    sp2, bp2 = get_file_paths('bbb/ccc.html')
    sp3, bp3 = get_file_paths('ddd.html')
    create_file(sp1, HTML)
    create_file(sp2, HTML)
    create_file(sp3, HTML)

    c.build()
    
    bpindex = get_build_path('_index.html')
    page = read_content(bpindex)
    assert 'href="aaa.html"' in page
    assert 'href="bbb/ccc.html"' in page
    assert 'href="ddd.html"' in page


def test_build__index(c):
    setup_module()
    make_dirs(SOURCE_DIR, 'bbb')

    sp1, bp1 = get_file_paths('aaa.html')
    sp2, bp2 = get_file_paths('eee.html')
    sp3, bp3 = get_file_paths('bbb/aa.html')
    sp4, bp4 = get_file_paths('bbb/zz.html')
    sp5, bp5 = get_file_paths('bbb/ccc.html')
    sp6, bp6 = get_file_paths('ddd.html')
    sp7, bp7 = get_file_paths('bbb/bb.html')
    create_file(sp1, HTML)
    create_file(sp2, HTML)
    create_file(sp3, HTML)
    create_file(sp4, HTML)
    create_file(sp5, HTML)
    create_file(sp6, HTML)
    create_file(sp7, HTML)
    c.build()
    
    bpindex = get_build_path('_index.html')
    page = read_content(bpindex)
    assert page.find('href="aaa.html"') < page.find('href="ddd.html"')
    assert page.find('href="ddd.html"') < page.find('href="eee.html"')
    assert page.find('href="eee.html"') < page.find('href="bbb/aa.html"')
    assert page.find('href="bbb/aa.html"') < page.find('href="bbb/bb.html"')
    assert page.find('href="bbb/bb.html"') < page.find('href="bbb/ccc.html"')
    assert page.find('href="bbb/ccc.html"') < page.find('href="bbb/zz.html"')


def test_build__index_txt(c):
    setup_module()
    make_dirs(SOURCE_DIR, 'bbb')

    sp1, bp1 = get_file_paths('aaa.html')
    sp2, bp2 = get_file_paths('eee.html')
    sp3, bp3 = get_file_paths('bbb/aa.html')
    sp4, bp4 = get_file_paths('bbb/zz.html')
    sp5, bp5 = get_file_paths('bbb/ccc.html')
    sp6, bp6 = get_file_paths('ddd.html')
    sp7, bp7 = get_file_paths('bbb/bb.html')
    create_file(sp1, HTML)
    create_file(sp2, HTML)
    create_file(sp3, HTML)
    create_file(sp4, HTML)
    create_file(sp5, HTML)
    create_file(sp6, HTML)
    create_file(sp7, HTML)
    c.build()
    
    bpindex = get_build_path('_index.txt')
    page = read_content(bpindex)
    assert page.find('http://0.0.0.0:8080/aaa.html') \
        < page.find('http://0.0.0.0:8080/ddd.html')
    assert page.find('http://0.0.0.0:8080/ddd.html') \
        < page.find('http://0.0.0.0:8080/eee.html')
    assert page.find('http://0.0.0.0:8080/eee.html') \
        < page.find('http://0.0.0.0:8080/bbb/aa.html')
    assert page.find('http://0.0.0.0:8080/bbb/aa.html') \
        < page.find('http://0.0.0.0:8080/bbb/bb.html')
    assert page.find('http://0.0.0.0:8080/bbb/bb.html') \
        < page.find('http://0.0.0.0:8080/bbb/ccc.html')
    assert page.find('http://0.0.0.0:8080/bbb/ccc.html') \
        < page.find('http://0.0.0.0:8080/bbb/zz.html')


def test_do_not_include_non_template_files_in__index(c):
    setup_module()
    bpindex = get_build_path('_index.html')

    sp = get_source_path('main.js')
    create_file(sp, "/* {% foobar %} */")
    c.build()
    page = read_content(bpindex)
    assert 'href="main.js"' not in page


def test_setting_filter_fragments_in__index(c):
    setup_module()
    bpindex = get_build_path('_index.html')

    create_file(get_source_path('bbb.html'), u'lalala')

    c.settings['FILTER_PARTIALS'] = True
    c.build()
    page = read_content(bpindex)
    assert 'href="bbb.html"' not in page

    c.settings['FILTER_PARTIALS'] = False
    c.build()
    page = read_content(bpindex)
    assert 'href="bbb.html"' in page


def test_setting_force_fragment_inclusion_in__index(c):
    setup_module()
    bpindex = get_build_path('_index.html')

    name = 'fragment.html'
    create_file(get_source_path(name), u'lalala')

    c.settings['FILTER_PARTIALS'] = True
    c.settings['INCLUDE'] = [name,]
    c.build()
    page = read_content(bpindex)
    assert 'href="%s"' % name in page


def test_setting_force_ignore_in__index(c):
    setup_module()
    bpindex = get_build_path('_index.html')

    name = 'fullpage.html'
    create_file(get_source_path(name), HTML)

    c.settings['FILTER_PARTIALS'] = True
    c.settings['FILTER'] = [name,]
    c.build()
    page = read_content(bpindex)
    assert 'href="%s"' % name not in page


def test_setting_force_ignore_in__index_with_patterns(c):
    setup_module()
    make_dirs(SOURCE_DIR, 'b')

    sp1, bp1 = get_file_paths('a.html')
    sp2, bp2 = get_file_paths('b/aa.html')
    sp3, bp3 = get_file_paths('b/z.html')
    sp4, bp4 = get_file_paths('b/ab.html')
    create_file(sp1, HTML)
    create_file(sp2, HTML)
    create_file(sp3, HTML)
    create_file(sp4, HTML)
    c.settings['FILTER'] = ['b/a*']
    c.build()

    bpindex = get_build_path('_index.html')
    page = read_content(bpindex)
    assert page.find('href="a.html"') != -1
    assert page.find('href="b/z.html"') != -1
    assert page.find('href="b/aa.html"') == -1
    assert page.find('href="b/ab.html"') == -1


@pytest.mark.fail
def test_setting_force_inclusion_in__index_with_patterns(c):
    setup_module()
    make_dirs(SOURCE_DIR, 'b')

    sp1, bp1 = get_file_paths('aaa.html')
    sp2, bp2 = get_file_paths('aab.html')
    sp3, bp3 = get_file_paths('abc.html')
    sp4, bp4 = get_file_paths('add.html')

    sp5, bp5 = get_file_paths('zoo.html')
    sp6, bp6 = get_file_paths('foo.html')
    sp7, bp7 = get_file_paths('b/loremipsum-oo.html')

    create_file(sp1, HTML)
    create_file(sp2, HTML)
    create_file(sp3, HTML)
    create_file(sp4, HTML)
    create_file(sp5, HTML)
    create_file(sp6, HTML)
    create_file(sp7, HTML)

    c.settings['FILTER'] = ['a*', '*oo.html']
    c.settings['INCLUDE'] = ['aa*', 'b/loremipsum*']
    c.build()

    bpindex = get_build_path('_index.html')
    page = read_content(bpindex)
    assert page.find('href="aaa.html"') != -1
    assert page.find('href="aab.html"') != -1
    assert page.find('href="b/loremipsum-oo.html"') != -1
    assert page.find('href="abc.html"') == -1
    assert page.find('href="add.html"') == -1

    for path in (bp1, bp2, bp7):
        assert read_content(path) == HTML


def test_feedback_message(c):
    setup_module()

    n1 = 'aa.html'
    n2 = 'bb.html'
    n3 = 'cc.txt'
    n4 = 'dd.txt.tmpl'
    create_file(get_source_path(n1), HTML)
    create_file(get_source_path(n2), HTML)
    create_file(get_source_path(n3), u'lalala')
    create_file(get_source_path(n4), u'lalala')
    c.settings['FILTER_PARTIALS'] = True

    msg = execute_and_read_stdout(c.build)

    assert n1 in msg
    assert n2 in msg
    assert n3 in msg
    assert n4 not in msg
