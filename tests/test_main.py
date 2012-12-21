# -*- coding: utf-8 -*-
import shutil
from clay.main import SOURCE_NOT_FOUND_HELP
from tests.helpers import *


HTML_PAGE = u'<!DOCTYPE html><html><head><title></title></head><body></body></html>'
TEXT = u'''Je suis belle, ô mortels! comme un rêve de pierre,
Et mon sein, où chacun s'est meurtri tour à tour,
Est fait pour inspirer au poète un amour'''


def setup_module():
    make_dirs(SOURCE_DIR)


def teardown_module():
    remove_dir(SOURCE_DIR)


def assert_page(t, name, content=HTML_PAGE, url=None, encoding='utf8'):
    sp = get_source_path(name)
    content = content.encode(encoding)
    create_file(sp, content, encoding=encoding)
    url = url or '/' + name
    
    resp = t.get(url)
    assert resp.status_code == HTTP_OK
    assert content == resp.data

    remove_file(sp)


def test_setup_with_filename_as_root():
    assert Clay(__file__)


def test_setup_with_settings():
    c = Clay(TESTS, {'foo': 'bar'})
    assert 'foo' in c.settings


def test_load_settings_from_file(c):
    assert 'foo' not in c.settings
    stpath = join(TESTS, 'settings.yml')
    create_file(stpath, '\nfoo: bar\n')
    c.load_settings_from_file()
    remove_file(stpath)
    assert 'foo' in c.settings


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
    assert resp.mimetype == 'text/html'


def test_notfound_page(t):
    resp = t.get('/lalalala.html')
    assert resp.status_code == HTTP_NOT_FOUND
    assert '<!-- not found -->' in resp.data
    assert resp.mimetype == 'text/html'


def test_settings_as_template_context():
    c = Clay(TESTS, {'who': u'world'})
    t = c.get_test_client()
    create_file(get_source_path('hello.html'), u'Hello {{ who }}!')
    resp = t.get('/hello.html')
    assert resp.status_code == HTTP_OK
    assert resp.data == 'Hello world!'
    assert resp.mimetype == 'text/html'


def test_can_run(c):
    def fake_run(**kwargs):
        return kwargs

    _run = c.app.run
    c.app.run = fake_run
    config = c.run()
    c.app.run = _run
    assert config['use_debugger']
    assert not config['use_reloader']


def test_run_with_custom_host_and_port(c):
    def fake_run(**kwargs):
        return kwargs

    _run = c.app.run
    c.app.run = fake_run
    host = 'localhost'
    port = 9000
    config = c.run(host=host, port=port)
    c.app.run = _run
    assert host == config['host']
    assert port == config['port']


def test_fail_if_source_dir_dont_exists(c):
    def fake_run(**kwargs):
        return kwargs

    remove_dir(SOURCE_DIR)
    _run = c.app.run
    c.app.run = fake_run
    
    out = execute_and_read_stdout(c.run)

    c.app.run = _run
    make_dirs(SOURCE_DIR)

    assert SOURCE_NOT_FOUND_HELP in out

