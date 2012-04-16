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


# SRC_SCSS = """
# @option compress: no;
# $main-color: #ce4dd6;
# $style: solid;
# $side: bottom;
# #navbar {
#   border-#{$side}: {
#     color: $main-color;
#     style: $style;
#   }
# }
# """.strip()


# EXPECTED_SCSS = """
# #navbar {
#   border-bottom-color: #ce4dd6;
#   border-bottom-style: solid;
# }
# """.strip()


FILENAME_IN = 'test.md'
FILENAME_OUT = 'test.html'


# SRC_HTML = """
# <link rel="stylesheet" href="foo/bar/%s" />
# <p class="scss"></p>""" % FILENAME_IN

# EXPECTED_HTML = """
# <link rel="stylesheet" href="foo/bar/%s" />
# <p class="scss"></p>""" % FILENAME_OUT


def test_markdown_enabled():
    assert p_markdown.enabled


# def test_scss_render():
#     filepath = make_view(FILENAME_IN, SRC_SCSS)
#     try:
#         resp = c.get('/' + FILENAME_IN)
#         content = resp.data.strip()
#         assert content == EXPECTED_SCSS
#     finally:
#         remove_file(filepath)


# def test_scss_build():
#     filepath = make_view(FILENAME_IN, SRC_SCSS)
#     filepath_out = get_build_filepath(FILENAME_OUT)
#     try:
#         clay_.build()
#         content = read_file(filepath_out).strip()
#         assert content == EXPECTED_SCSS
#     finally:
#         remove_file(filepath)
#         remove_file(filepath_out)


# def test_scss_html_replace():
#     static_filepath = make_view(FILENAME_IN, SRC_SCSS)
#     filepath_out = get_build_filepath(FILENAME_OUT)
#     html_filename = 'test_scss.html'
#     html_filepath = make_view(html_filename, SRC_HTML)
#     html_filepath_out = get_build_filepath(html_filename)
#     try:
#         clay_.build()
#         content = read_file(html_filepath_out)
#         assert content == EXPECTED_HTML
#     finally:
#         remove_file(static_filepath)
#         remove_file(filepath_out)
#         remove_file(html_filepath)
#         remove_file(html_filepath_out)

