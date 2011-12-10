# -*- coding: utf-8 -*-
import shutil

from clay.processors import coffeescript_
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


def test_coffeescript_enabled():
    from clay.render import enabled_processors

    assert coffeescript_.enabled
    for ext in coffeescript_.extensions_in:
        assert ext in enabled_processors


def test_coffeescript_render():
    filepath = make_view(FILENAME_IN, SRC_COFFEESCRIPT)

    resp = c.get('/' + FILENAME_IN)
    content = resp.data.strip()
    print content
    assert content == EXPECTED_COFFEESCRIPT

    remove_file(filepath)


def test_coffeescript_make():
    filepath = make_view(FILENAME_IN, SRC_COFFEESCRIPT)
    proto.build()
    filepath_out = get_build_filepath(FILENAME_OUT)

    content = read_file(filepath_out).strip()
    assert content == EXPECTED_COFFEESCRIPT
    remove_file(filepath)
    remove_file(filepath_out)


def test_coffeescript_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_COFFEESCRIPT)
    filepath_out = get_build_filepath(FILENAME_OUT)

    html_filename = 'test_coffee.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    proto.build()
    html_filepath_out = get_build_filepath(html_filename)

    content = read_file(html_filepath_out)
    print content
    assert content == EXPECTED_HTML

    remove_file(static_filepath)
    remove_file(filepath_out)
    remove_file(html_filepath)

