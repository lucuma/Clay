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
    'HOST': '0.0.0.0',
    'PORT': 8080,

    'PLAIN_TEXT': ['.js', ],
    'VIEWS_IGNORE': ['base.html', ],
    'VIEWS_LIST_IGNORE': ['base.html', ],

    'PRE_PROCESSORS': [], #['scss', 'less', 'coffee', 'markdown']
    'POST_PROCESSORS': [], #['pygments']

    'LAYOUTS': '',
}

app_settings = {
    'RELOADER': False,
    'DEBUG': True,
}

