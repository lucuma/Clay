# -*- coding: utf-8 -*-
import shutil

from clay import p_markdown
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


SRC_MARKDOWN = """
# Introduction

Markdown is a text-to-HTML conversion tool for web writers.
See the [Syntax](http://daringfireball.net/projects/markdown/syntax) page for details.
""".strip()

EXPECTED_MARKDOWN = """
<h1 id="introduction"><a class="toclink" href="#introduction">Introduction</a></h1>
<p>Markdown is a text-to-HTML conversion tool for web writers.<br>
See the <a href="http://daringfireball.net/projects/markdown/syntax">Syntax</a> page for details.</p>
""".strip()

FILENAME_IN = 'test.md'
FILENAME_OUT = 'test.html'

HTML = """<a href="foo/bar/%s" />
<p class="md"></p>"""

SRC_HTML = HTML % FILENAME_IN
EXPECTED_HTML = HTML % FILENAME_OUT


def test_markdown_render():
    filepath = make_view(FILENAME_IN, SRC_MARKDOWN)
    try:
        resp = c.get('/' + FILENAME_IN)
        content = resp.data.strip()
        assert content == EXPECTED_MARKDOWN
    finally:
        remove_file(filepath)


def test_markdown_build():
    filepath = make_view(FILENAME_IN, SRC_MARKDOWN)
    filepath_out = get_build_filepath(FILENAME_OUT)
    try:
        clay_.build()
        content = read_file(filepath_out).strip()
        assert content == EXPECTED_MARKDOWN
    finally:
        remove_file(filepath)
        remove_file(filepath_out)


def test_markdown_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_MARKDOWN)
    filepath_out = get_build_filepath(FILENAME_OUT)
    html_filename = 'test_md.html'
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

