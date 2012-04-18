# -*- coding: utf-8 -*-
"""
    # Clay.pp_typogrify

    Applies the following filters: widont, dashes, ellipses, quotes, caps,
    amp and initial_quotes.

"""
from .typogrify import typogrify


enabled = True

def process(html):
    return typogrify(html)
