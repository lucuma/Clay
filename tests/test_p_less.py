# -*- coding: utf-8 -*-
import shutil

from clay.processors import less_
import pytest

from tests.utils import *


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


SRC_HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>""" % FILENAME_IN


EXPECTED_HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>""" % FILENAME_OUT


def test_less_enabled():
    from clay.render import enabled_processors

    assert less_.enabled
    for ext in less_.extensions_in:
        assert ext in enabled_processors


def test_less_render():
    filepath = make_view(FILENAME_IN, SRC_LESS)

    resp = c.get('/' + FILENAME_IN)
    content = resp.data.strip()
    assert content == EXPECTED_LESS

    remove_file(filepath)


def test_less_make():
    filepath = make_view(FILENAME_IN, SRC_LESS)
    proto.build()
    filepath_out = get_build_filepath(FILENAME_OUT)

    content = read_file(filepath_out).strip()
    assert content.strip() == EXPECTED_LESS
    remove_file(filepath)
    remove_file(filepath_out)


def test_less_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_LESS)
    filepath_out = get_build_filepath(FILENAME_OUT)

    html_filename = 'test_less.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    proto.build()
    html_filepath_out = get_build_filepath(html_filename)

    content = read_file(html_filepath_out)
    assert content == EXPECTED_HTML

    remove_file(static_filepath)
    remove_file(filepath_out)
    remove_file(html_filepath)

