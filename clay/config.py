# -*- coding: utf-8 -*-
"""
# Clay.config

"""

SOURCE_DIR = 'source'
BUILD_DIR = 'build'
VIEWS_INDEX = '_index.html'

IGNORE = ('.', '_')

default_settings = {
    'host': '0.0.0.0',
    'port': 8080,

    'views_list_ignore': [],

    'pre_processors': ['scss', 'less', 'coffee', 'markdown'],
    'post_processors': ['pygments', 'typogrify'],

    'theme_prefix': '',
}


