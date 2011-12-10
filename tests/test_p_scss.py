# -*- coding: utf-8 -*-
import shutil

from clay.processors import scss_
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


SRC_SCSS = """
@option compress: no;
$main-color: #ce4dd6;
$style: solid;
$side: bottom;
#navbar {
  border-#{$side}: {
    color: $main-color;
    style: $style;
  }
}
""".strip()


EXPECTED_SCSS = """
#navbar {
  border-bottom-color: #ce4dd6;
  border-bottom-style: solid;
}
""".strip()


FILENAME_IN = 'sassy.scss'
FILENAME_OUT = 'sassy.css'


SRC_HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>""" % FILENAME_IN


EXPECTED_HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>""" % FILENAME_OUT



def test_scss_enabled():
    from clay.render import enabled_processors

    assert scss_.enabled
    for ext in scss_.extensions_in:
        assert ext in enabled_processors


def test_scss_render():
    filepath = make_view(FILENAME_IN, SRC_SCSS)

    resp = c.get('/' + FILENAME_IN)
    content = resp.data.strip()
    assert content == EXPECTED_SCSS

    remove_file(filepath)


def test_scss_build():
    filepath = make_view(FILENAME_IN, SRC_SCSS)
    proto.build()
    filepath_out = get_build_filepath(FILENAME_OUT)

    content = read_file(filepath_out).strip()
    assert content == EXPECTED_SCSS

    remove_file(filepath)
    remove_file(filepath_out)


def test_scss_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_SCSS)
    filepath_out = get_build_filepath(FILENAME_OUT)

    html_filename = 'test_scss.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    proto.build()
    html_filepath_out = get_build_filepath(html_filename)

    content = read_file(html_filepath_out)
    assert content == EXPECTED_HTML

    remove_file(static_filepath)
    remove_file(filepath_out)
    remove_file(html_filepath)

