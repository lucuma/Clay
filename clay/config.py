# -*- coding: utf-8 -*-
"""
# Clay.config

"""
from os.path import abspath, join, dirname

SOURCE_DIR = u'source'
BUILD_DIR = u'build'
VIEWS_INDEX = u'_index.html'

DEFAULT_TEMPLATES = join(abspath(dirname(__file__)), u'source')

IGNORE = ('.', '_')

default_settings = {
    'host': '0.0.0.0',
    'port': 8080,

    'plain_text': ['.js', ],
    'views_ignore': [],
    'views_list_ignore': [],

    'pre_processors': ['scss', 'less', 'coffee', 'markdown'],
    'post_processors': ['pygments',],

    'theme_prefix': '',
}

app_settings = {
    'RELOADER': False,
}

