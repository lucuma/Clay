# -*- coding: utf-8 -*-
import shutil

from clay import p_less
import pytest

from tests.utils import *


def setup_module():
    try:
        shutil.rmtree(clay_.build_dir)
    except OSError:
        pass


def teardown_module():
    try:
        shutil.rmtree(clay_.build_dir)
    except OSError:
        pass


SRC_LESS = """
@the-border: 1px;
@base-color: #111;
@red: #842210;

#header {
  color: @base-color * 3;
  border-left: @the-border;
  border-right: @the-border * 2;
}

#footer {
  color: @base-color + #003300;
  border-color: desaturate(@red, 10%);
}
""".strip()


EXPECTED_LESS = """
#header {
  color: #333333;
  border-left: 1px;
  border-right: 2px;
}
#footer {
  color: #114411;
  border-color: #7d2717;
}
""".strip()


FILENAME_IN = 'less.less'
FILENAME_OUT = 'less.css'


BASE_HTML = HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>"""

SRC_HTML = BASE_HTML % FILENAME_IN
EXPECTED_HTML = BASE_HTML % FILENAME_OUT


def test_less_render():
    filepath = make_view(FILENAME_IN, SRC_LESS)
    try:
        resp = c.get('/' + FILENAME_IN)
        content = resp.data.strip()
        assert content == EXPECTED_LESS
    finally:
        remove_file(filepath)


def test_less_build():
    filepath = make_view(FILENAME_IN, SRC_LESS)
    filepath_out = get_build_filepath(FILENAME_OUT)
    clay_.settings['FILTER_PARTIALS'] = False
    try:
        clay_.build()
        content = read_file(filepath_out).strip()
        assert content.strip() == EXPECTED_LESS
    finally:
        remove_file(filepath)
        remove_file(filepath_out)


def test_less_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_LESS)
    filepath_out = get_build_filepath(FILENAME_OUT)
    html_filename = 'test_less.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    html_filepath_out = get_build_filepath(html_filename)
    try:
        clay_.build()
        content = read_file(html_filepath_out)
        assert content == EXPECTED_HTML
    finally:
        remove_file(static_filepath)
        remove_file(filepath_out)
        remove_file(html_filepath)
        remove_file(html_filepath_out)

