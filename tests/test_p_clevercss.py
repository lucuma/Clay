# -*- coding: utf-8 -*-
import shutil

from clay.processors import clevercss_
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


SRC_CLEVERCSS = """
ul#comments, ol#comments:
  margin: 0
  padding: 0

  li:
    padding: 0.4em
    margin: 0.8em 0 0.8em

    h3:
      font-size: 1.2em
    p:
      padding: 0.3em
    p.meta:
      text-align: right
""".strip()


EXPECTED_CLEVERCSS = """
ul#comments,
ol#comments {
  margin: 0;
  padding: 0;
}

ul#comments li,
ol#comments li {
  padding: 0.4em;
  margin: 0.8em 0 0.8em;
}

ul#comments li h3,
ol#comments li h3 {
  font-size: 1.2em;
}

ul#comments li p,
ol#comments li p {
  padding: 0.3em;
}

ul#comments li p.meta,
ol#comments li p.meta {
  text-align: right;
}
""".strip()


FILENAME_IN = 'clever.ccss'
FILENAME_OUT = 'clever.css'


SRC_HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>""" % FILENAME_IN


EXPECTED_HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>""" % FILENAME_OUT



def test_clevercss_enabled():
    from clay.render import enabled_processors

    assert clevercss_.enabled
    for ext in clevercss_.extensions_in:
        assert ext in enabled_processors


def test_clevercss_render():
    filepath = make_view(FILENAME_IN, SRC_CLEVERCSS)

    resp = c.get('/' + FILENAME_IN)
    content = resp.data.strip()
    assert content == EXPECTED_CLEVERCSS

    remove_file(filepath)


def test_clevercss_make():
    filepath = make_view(FILENAME_IN, SRC_CLEVERCSS)
    proto.build()
    filepath_out = get_build_filepath(FILENAME_OUT)

    content = read_file(filepath_out).strip()
    assert content == EXPECTED_CLEVERCSS
    remove_file(filepath)
    remove_file(filepath_out)


def test_clevercss_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_CLEVERCSS)
    filepath_out = get_build_filepath(FILENAME_OUT)

    html_filename = 'test_clevercss.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    proto.build()
    html_filepath_out = get_build_filepath(html_filename)

    content = read_file(html_filepath_out)
    assert content == EXPECTED_HTML

    remove_file(static_filepath)
    remove_file(filepath_out)
    remove_file(html_filepath)

