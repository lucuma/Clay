# -*- coding: utf-8 -*-
"""
    # Clay.config
"""

SOURCE_DIR = 'src'
BUILD_DIR = 'build'
VIEWS_INDEX = '_index.html'

IGNORE = ('.', '_')

default_settings = {
    'views_list_ignore': [],

    # CoffeeScript settings
    'coffee_bare': True,
    
    # Markdown settings 
    'markdown_extensions': [
        # Abbreviations
        'abbr',
        # Definition lists
        'def_list',
        # Footnotes
        'footnotes',
        # Fenced code blocks
        'fenced_code',
        # HeaderId
        'headerid',
        # Tables
        'tables',
        # Code highlighting using using Pygments
        'codehilite',
        # Treat newlines as hard breaks (like StackOverflow and GitHub).
        'nl2br',
        # Table of Contents
        'toc',
        # Meta-Data
        'meta',
    ], 
    'markdown_safe_mode': False,
    'markdown_output_format': 'xhtml1',

    'host': '0.0.0.0',
    'port': 8080,
}


