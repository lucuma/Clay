# -*- coding: utf-8 -*-
"""
# Clay.config

"""
import os

SOURCE_DIR = 'source'
BUILD_DIR = 'build'
VIEWS_INDEX = '_index.html'

DEFAULT_TEMPLATES = os.path.join(os.path.dirname(__file__), 'source')

IGNORE = ('.', '_')

default_settings = {
    'host': '0.0.0.0',
    'port': 8080,

    'plain_text': ['.js', ],
    'views_list_ignore': [],

    'pre_processors': ['scss', 'less', 'coffee', 'markdown'],
    'post_processors': ['pygments', 'typogrify'],

    'theme_prefix': '',
}


