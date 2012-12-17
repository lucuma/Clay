# -*- coding: utf-8 -*-
import shutil

from tests.helpers import *


HTML_PAGE = u'<!DOCTYPE html><html><head><title></title></head><body></body></html>'
TEXT = u'''Je suis belle, ô mortels! comme un rêve de pierre,
Et mon sein, où chacun s'est meurtri tour à tour,
Est fait pour inspirer au poète un amour'''


def setup_module():
    try:
        shutil.rmtree(SOURCE_DIR)
    except OSError:
        pass
    make_dirs(SOURCE_DIR)


def teardown_module():
    try:
        shutil.rmtree(SOURCE_DIR)
    except OSError:
        pass


def assert_page(t, name, content=HTML_PAGE, url=None, encoding='utf8'):
    content = content.encode(encoding)
    path = get_source_path(name)
    create_file(path, content, encoding=encoding)
    url = url or '/' + name
    resp = t.get(url)
    assert resp.status_code == HTTP_OK
    assert content == resp.data


def test_setup_with_filename_as_root():
    assert Clay(__file__)


def test_render_page(t):
    assert_page(t, 'index.html')


def test_index_page(t):
    assert_page(t, 'index.html', url='/')


def test_render_sub_page(t):
    make_dirs(join(SOURCE_DIR, 'sub'))
    assert_page(t, 'sub/index.html')


def test_render_sub_index_page(t):
    make_dirs(join(SOURCE_DIR, 'sub'))
    assert_page(t, 'sub/index.html', url='sub')


def test_do_not_process_non_html_or_tmpl_files(t):
    assert_page(t, 'main.js', "/* {% foobar %} */")


def test_i18n_filename(t):
    assert_page(t, 'mañana.txt', TEXT)


def test_weird_encoding_of_content(t):
    assert_page(t, 'iso-8859-1.txt', TEXT, encoding='iso-8859-1')


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


def test_notfound_page(t):
    resp = t.get('/lalalala.html')
    assert resp.status_code == HTTP_NOT_FOUND
    assert '<title>Page not found</title>' in resp.data


def test_settings_as_template_context():
    root = dirname(__file__)
    c = Clay(root, {'who': u'world'})
    t = c.get_test_client()
    create_file(get_source_path('hello.html'), u'Hello {{ who }}!')
    resp = t.get('/hello.html')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'Hello world!'


def test_can_run(c):
    config = c.run(_test=True)
    assert config['use_debugger']
    assert not config['use_reloader']


def test_run_with_custom_host_and_port(c):
    host = 'localhost'
    port = 9000
    config = c.run(host=host, port=port, _test=True)
    assert host == config['host']
    assert port == config['port']

