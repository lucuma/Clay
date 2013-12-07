# -*- coding: utf-8 -*-
from __future__ import print_function

from clay import Clay

from .helpers import *


TEXT = u'''Je suis belle, ô mortels! comme un rêve de pierre,
Et mon sein, où chacun s'est meurtri tour à tour,
Est fait pour inspirer au poète un amour'''


def assert_page(t, name, content=HTML, url=None, encoding='utf8'):
    create_page(name, content, encoding)
    url = url or '/' + name
    resp = t.get(url)
    assert resp.status_code == HTTP_OK
    assert content.encode(encoding) == resp.data


def test_setup_with_filename_as_root():
    assert Clay(__file__)


def test_setup_with_settings():
    c = Clay(TESTS, {'foo': 'bar'})
    assert 'foo' in c.settings


def test_get_real_fn(c):
    assert c.get_real_fn('foo/bar/test.html') == 'test.html'
    assert c.get_real_fn('foo/bar/test.txt') == 'test.txt'
    assert c.get_real_fn('foo/bar/test.txt.tmpl') == 'test.txt'


def test_guess_mimetype(c):
    assert c.guess_mimetype('lalala.html') == 'text/html'
    assert c.guess_mimetype('lalala.txt') == 'text/plain'
    assert c.guess_mimetype('whatever') == 'text/plain'


def test_load_settings_from_file():
    c = Clay(TESTS)
    assert 'foo' not in c.settings

    stpath = join(TESTS, 'settings.py')
    create_file(stpath, "\nfoo='bar'\n")
    c = Clay(TESTS)
    remove_file(stpath)
    assert 'foo' in c.settings


def test_render_page(t):
    assert_page(t, 'index.html')


def test_index_page(t):
    assert_page(t, 'index.html', url='/')


def test_render_sub_page(t):
    assert_page(t, 'sub/index.html')


def test_render_sub_index_page(t):
    assert_page(t, 'sub/index.html', url='sub')


def test_ignore_non_template_files(t):
    assert_page(t, 'main.js', "/* {% foobar %} */")


def test_i18n_filename(t):
    assert_page(t, 'mañana.txt', TEXT)


def test_weird_encoding_of_content(t):
    assert_page(t, 'iso-8859-1.txt', TEXT, encoding='iso-8859-1')


def test_static_filename(t):
    assert_page(t, 'static/css/index.css', u'')


def test_process_template_files(t):
    content = """
    {% for i in range(1,5) -%}
    .icon{{ i }} { background-image: url('img/icon{{ i }}.png'); }
    {% endfor -%}
    """
    expected = """
    .icon1 { background-image: url('img/icon1.png'); }
    .icon2 { background-image: url('img/icon2.png'); }
    .icon3 { background-image: url('img/icon3.png'); }
    .icon4 { background-image: url('img/icon4.png'); }
    """
    path = get_source_path('main.css.tmpl')
    create_file(path, content)
    resp = t.get('/main.css.tmpl')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/css'
    assert resp.data.strip() == expected.strip()


def test_page_with_includes(t):
    create_file(get_source_path('foo.html'), u'foo{% include "bar.html" %}')
    create_file(get_source_path('bar.html'), u'bar')
    resp = t.get('/foo.html')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'foobar'
    assert resp.mimetype == 'text/html'


def test_settings_as_template_context():

    c = Clay(TESTS, {'who': u'world'})
    t = c.get_test_client()
    create_file(get_source_path('hello.html'), u'Hello {{ who }}!')
    resp = t.get('/hello.html')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'Hello world!'
    assert resp.mimetype == 'text/html'


def test_values_as_template_context():
    c = Clay(TESTS)
    t = c.get_test_client()
    create_file(get_source_path('hello.html'), u'Hello {{ who }}!')
    resp = t.get('/hello.html?who=world')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'Hello world!'
    assert resp.mimetype == 'text/html'


def test_get_pages_list(c):
    make_dirs(SOURCE_DIR, 'bbb')

    create_file(get_source_path('aaa.html'), HTML)
    create_file(get_source_path('bbb/ccc.html'), HTML)
    create_file(get_source_path('lalala.txt'), u'')

    expected = ['aaa.html', 'bbb/ccc.html', 'lalala.txt']
    expected.sort()
    result = c.get_pages_list()
    result.sort()
    print(result)
    assert expected == result


def test_show__index_txt(t):
    make_dirs(SOURCE_DIR, 'bbb')

    create_file(get_source_path('aaa.html'), HTML)
    create_file(get_source_path('bbb/ccc.html'), HTML)
    create_file(get_source_path('lalala.txt'), u'')

    resp = t.get('/_index.txt')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'

    page = resp.data
    assert 'http://0.0.0.0:8080/aaa.html' in page
    assert 'http://0.0.0.0:8080/bbb/ccc.html' in page
    assert 'href="aaa.html"' not in page
    assert 'lalala.txt' not in page


def test_show__index(t):
    make_dirs(SOURCE_DIR, 'bbb')

    create_file(get_source_path('aaa.html'), HTML)
    create_file(get_source_path('bbb/ccc.html'), HTML)
    create_file(get_source_path('ddd.html'), HTML)

    resp = t.get('/_index.html')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'

    page = resp.data
    assert 'href="aaa.html"' in page
    assert 'href="bbb/ccc.html"' in page
    assert 'href="ddd.html"' in page


def test__index_is_sorted(t):
    make_dirs(SOURCE_DIR, 'bbb')

    create_file(get_source_path('bbb.html'), HTML)
    create_file(get_source_path('bbb/aa.html'), HTML)
    create_file(get_source_path('bbb/ccc.html'), HTML)
    create_file(get_source_path('aaa.html'), HTML)
    create_file(get_source_path('ddd.html'), HTML)

    resp = t.get('/_index.html')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'

    page = resp.data
    assert page.find('href="aaa.html"') < page.find('href="bbb.html"')
    assert page.find('href="bbb.html"') < page.find('href="ddd.html"')
    assert page.find('href="ddd.html"') < page.find('href="bbb/aa.html"')
    assert page.find('href="bbb/aa.html"') < page.find('href="bbb/ccc.html"')


def test_do_not_include_non_template_files_in__index(t):
    create_file(get_source_path('main.js'), "/* {% foobar %} */")
    resp = t.get('/_index.html')
    assert 'href="main.js"' not in resp.data


def test_setting_filter_fragments_in__index(c):
    t = c.get_test_client()

    create_file(get_source_path('aaa.html'), HTML)
    create_file(get_source_path('bbb.html'), u'lalala')

    c.settings['FILTER_PARTIALS'] = True
    resp = t.get('/_index.html')
    page = resp.data
    assert 'href="aaa.html"' in page
    assert 'href="bbb.html"' not in page

    c.settings['FILTER_PARTIALS'] = False
    resp = t.get('/_index.html')
    page = resp.data
    assert 'href="aaa.html"' in page
    assert 'href="bbb.html"' in page


def test_setting_filter_fragments_in__indexs_after_rendering(c):
    t = c.get_test_client()

    create_file(get_source_path('base.html'),
        u'<!DOCTYPE html><html><body>{% block content %}{% endblock %}</body></html>')
    create_file(get_source_path('xxx.html'),
        u'{% extends "base.html" %}{% block content %}Hi!{% endblock %}')

    c.settings['FILTER_PARTIALS'] = True
    resp = t.get('/_index.html')
    page = resp.data
    assert 'href="base.html"' in page
    assert 'href="xxx.html"' in page


def test_setting_force_fragment_inclusion_in__index(c):
    t = c.get_test_client()

    name = 'fragment.html'
    create_file(get_source_path(name), u'lalala')

    c.settings['FILTER_PARTIALS'] = True
    c.settings['INCLUDE'] = [name, ]
    resp = t.get('/_index.html')
    assert 'href="%s"' % name in resp.data


def test_setting_force_ignore_in__index(c):
    t = c.get_test_client()

    name = 'fullpage.html'
    create_file(get_source_path(name), HTML)

    c.settings['FILTER_PARTIALS'] = True
    c.settings['FILTER'] = [name, ]
    resp = t.get('/_index.html')
    assert not 'href="%s"' % name in resp.data


def test_setting_force_ignore_in__index_with_patterns(c):
    make_dirs(SOURCE_DIR, 'b')

    create_file(get_source_path('a.html'), HTML)
    create_file(get_source_path('b.html'), HTML)

    create_file(get_source_path('b/c.html'), HTML)
    create_file(get_source_path('b/ab.html'), HTML)
    create_file(get_source_path('b/a-a.html'), HTML)

    create_file(get_source_path('zoo.html'), HTML)
    create_file(get_source_path('foo.html'), HTML)
    create_file(get_source_path('b/loremipsum-oo.html'), HTML)

    t = c.get_test_client()
    c.settings['FILTER'] = ['b/a*', '*oo.html']
    resp = t.get('/_index.html')

    assert 'href="a.html"' in resp.data
    assert 'href="b.html"' in resp.data
    assert 'href="b/aa.html"' not in resp.data
    assert 'href="b/c.html"' in resp.data
    assert 'href="b/ab.html"' not in resp.data

    assert 'href="zoo.html"' not in resp.data
    assert 'href="foo.html"' not in resp.data
    assert 'href="b/loremipsum-oo.html"' not in resp.data


def test_setting_force_inclusion_in__index_with_patterns(c):
    make_dirs(SOURCE_DIR, 'b')

    create_file(get_source_path('aaa.html'), HTML)
    create_file(get_source_path('aab.html'), HTML)
    create_file(get_source_path('abc.html'), HTML)
    create_file(get_source_path('add.html'), HTML)

    create_file(get_source_path('zoo.html'), HTML)
    create_file(get_source_path('foo.html'), HTML)
    create_file(get_source_path('b/loremipsum-oo.html'), HTML)

    t = c.get_test_client()
    c.settings['FILTER'] = ['a*', '*oo.html']
    c.settings['INCLUDE'] = ['aa*', 'b/loremipsum*']
    resp = t.get('/_index.html')

    assert 'href="aaa.html"' in resp.data
    assert 'href="aab.html"' in resp.data
    assert 'href="abc.html"' not in resp.data
    assert 'href="add.html"' not in resp.data

    assert 'href="zoo.html"' not in resp.data
    assert 'href="foo.html"' not in resp.data
    assert 'href="b/loremipsum-oo.html"' in resp.data
