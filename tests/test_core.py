# -*- coding: utf-8 -*-
import io
import os
import shutil

from clay import Clay
import pytest

from .utils import *


def setup_module():
    try:
        shutil.rmtree(proto.build_dir)
    except OSError:
        pass


def teardown_module():
    try:
        shutil.rmtree(proto.build_dir)
    except OSError:
        pass


def test_common():
    resp = c.get('/index.html')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    assert len(resp.data) > 100


def test_view_not_found():
    resp = c.get('/qwertyuiop.bar')
    assert '<!-- not found -->' in resp.data
    assert resp.status_code == HTTP_NOT_FOUND
    assert resp.mimetype == 'text/html'


def test_render_non_ascii_filenames():
    resp = c.get(u'/mañana.txt')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'


def test_render_non_utf8_content():
    resp = c.get('/iso-8859-1.txt')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/plain'


def test_build():
    try:
        shutil.rmtree(proto.build_dir)
    except OSError:
        pass
    proto.build()

    assert os.path.isdir(proto.build_dir)
    path = os.path.join(proto.build_dir, 'index.html')
    assert os.path.isfile(path)


def test_build_overwrite():
    filename = os.path.join(proto.build_dir, 'index.html')
    bad_data = u':('
    make_file(filename, bad_data)
    proto.build()
    
    new_data = read_file(filename)
    assert new_data != bad_data


def test_build_absolute2relative():
    filename1 = os.path.join(proto.build_dir, 'index.html')
    filename2 = os.path.join(proto.build_dir, 'foo', 'index.html')
    proto.build()

    c1 = read_file(filename1)
    assert '<link href="styles/test.css"' in c1
    c2 = read_file(filename2)
    assert '<link href="../styles/test.css"' in c2

