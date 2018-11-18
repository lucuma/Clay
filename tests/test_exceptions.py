# coding=utf-8
from clay import Clay
from clay.main import SOURCE_NOT_FOUND
import pytest

from .conftest import setup_function, teardown_function  # noqa
from .helpers import (
    create_file, get_source_path, remove_dir, execute_and_read_stdout,
    make_dirs, create_page, SOURCE_DIR, HTTP_NOT_FOUND, TESTS, HTML
)


def test_friendly_notfound_of_templates(t):
    create_file(get_source_path('foo.html'), u'foo{% include "barbar.html" %}')

    resp = t.get('/hello.html')
    assert resp.status_code == HTTP_NOT_FOUND
    data = resp.data.decode()
    assert 'hello.html' in data
    assert 'jinja2.exceptions' not in data

    resp = t.get('/foo.html')
    data = resp.data.decode()
    assert resp.status_code == HTTP_NOT_FOUND
    assert 'barbar.html' in data
    assert 'jinja2.exceptions' not in data


def test_friendly_notfound_of_files(t):
    resp = t.get('/foobar')
    data = resp.data.decode()
    assert resp.status_code == HTTP_NOT_FOUND
    assert 'foobar' in data
    assert 'jinja2.exceptions' not in data


def test_fail_if_source_dir_dont_exists(c):
    remove_dir(SOURCE_DIR)

    def fake_run(**kwargs):
        return kwargs

    _run = c.app.run
    c.app.run = fake_run
    out = execute_and_read_stdout(c.run)

    c.app.run = _run
    make_dirs(SOURCE_DIR)

    assert SOURCE_NOT_FOUND in out


def test_make_dirs_wrong():
    with pytest.raises(OSError):
        make_dirs('/etc/bla')


def test_fix_settings():
    bad_settings = dict(
        FILTER_PARTIALS=None,
        FILTER=None,
        INCLUDE=None,
        HOST=None,
        PORT=None,
    )
    c = Clay(TESTS, bad_settings)
    create_page('test.html', HTML)
    c.get_pages_index()
