# -*- coding: utf-8 -*-
import shutil

from clay import p_coffee
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


SRC_COFFEESCRIPT = """
square = (x) -> x * x
cube   = (x) -> square(x) * x
""".strip()


EXPECTED_COFFEESCRIPT = """
(function() {
  var cube, square;

  square = function(x) {
    return x * x;
  };

  cube = function(x) {
    return square(x) * x;
  };

}).call(this);
""".strip()


FILENAME_IN = 'coffee-script.coffee'
FILENAME_OUT = 'coffee-script.js'


SRC_HTML = """
<script src="foo/bar/%s"></script>
<p class="coffee"></p>""" % FILENAME_IN


EXPECTED_HTML = """
<script src="foo/bar/%s"></script>
<p class="coffee"></p>""" % FILENAME_OUT


def test_coffeescript_render():
    filepath = make_view(FILENAME_IN, SRC_COFFEESCRIPT)

    resp = c.get('/' + FILENAME_IN)
    content = resp.data.strip()
    assert content == EXPECTED_COFFEESCRIPT

    remove_file(filepath)


def test_coffeescript_build():
    filepath = make_view(FILENAME_IN, SRC_COFFEESCRIPT)
    filepath_out = get_build_filepath(FILENAME_OUT)
    clay_.settings['FILTER_PARTIALS'] = False
    try:
        clay_.build()
        content = read_file(filepath_out).strip()
        assert content == EXPECTED_COFFEESCRIPT
    finally:
        remove_file(filepath)
        remove_file(filepath_out)


def test_coffeescript_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_COFFEESCRIPT)
    filepath_out = get_build_filepath(FILENAME_OUT)
    html_filename = 'test_coffee.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    html_filepath_out = get_build_filepath(html_filename)
    try:
        clay_.build()
        content = read_file(html_filepath_out)
        print content
        assert content == EXPECTED_HTML
    finally:
        remove_file(static_filepath)
        remove_file(filepath_out)
        remove_file(html_filepath)
        remove_file(html_filepath_out)

