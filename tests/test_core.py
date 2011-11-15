# -*- coding: utf-8 -*-
import io
import os

from clay import Clay
import pytest


proto = Clay(__file__)
c = proto.test_client()

HTTP_OK = 200
HTTP_NOT_FOUND = 404


def test_common():
    resp = c.get('/index.html')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    assert len(resp.data) > 100


def test_view_not_found():
    resp = c.get('/qwertyuiop.bar')
    assert resp.status_code == HTTP_NOT_FOUND


def test_render_non_ascii_filenames():
    resp = c.get(u'/mañana.txt')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'


def test_render_non_utf8_content():
    resp = c.get('/iso-8859-1.txt')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'


def test_render_static():
    filename = os.path.join(proto.static_dir, 'test.css')
    with io.open(filename) as f:
        expected = f.read()
    resp = c.get('/static/test.css')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/css'
    assert resp.data == expected


def test_make():
    try:
        os.remove(proto.build_dir)
    except OSError:
        pass
    proto.make()
    assert os.path.isdir(proto.build_dir)

    # Test overwrite
    filename = os.path.join(proto.build_dir, 'index.html')
    bad_data = u':('
    with io.open(filename, 'w+t') as f:
        f.write(bad_data)
    proto.make()
    with io.open(filename) as f:
        new_data = f.read()
    assert new_data != bad_data

