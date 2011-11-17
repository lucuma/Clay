# -*- coding: utf-8 -*-
import pytest

from .utils import *

import clevercss
from clay.processors import clevercss_


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
"""


EXPECTED_CLEVERCSS = """ul#comments,
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
}"""


SRC_HTML = """
<link rel="stylesheet" href="clever.ccss" />
<link href="clever.ccss" rel="stylesheet" />"""


EXPECTED_HTML = """
<link rel="stylesheet" href="clever.css" />
<link href="clever.css" rel="stylesheet" />"""


def test_clevercss_enabled():
    from clay.static import enabled_processors

    assert clevercss_.enabled
    for ext in clevercss_.extensions_in:
        assert ext in enabled_processors


def test_clevercss_render():
    filename = 'clever.ccss'
    filepath = make_static(filename, SRC_CLEVERCSS)

    resp = c.get('/static/' + filename)
    assert resp.data == EXPECTED_CLEVERCSS
    assert resp.mimetype == clevercss_.mimetype_out

    remove_file(filepath)


def test_clevercss_make():
    filename = 'clever.ccss'
    filepath = make_static(filename, SRC_CLEVERCSS)
    proto.make()
    filepath_out = get_static_filepath('clever.css')

    content = read_file(filepath_out)
    assert content == EXPECTED_CLEVERCSS
    remove_file(filepath)
    remove_file(filepath_out)


def test_html_replace():
    static_filename = 'clever.ccss'
    static_filepath = make_static(static_filename, SRC_CLEVERCSS)
    html_filename = 'test_clevercss.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    proto.make()
    html_filepath_out = get_build_filepath(html_filename)

    content = read_file(html_filepath_out)
    assert content == EXPECTED_HTML

    remove_file(static_filepath)
    remove_file(html_filepath)

