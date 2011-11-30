# -*- coding: utf-8 -*-
"""
    # Clay.processors.scss

    Sassy CSS processor

    http://sass-lang.com/
    https://github.com/Kronuz/pyScss

"""
from ..libs import scss
from ..utils import get_source


enabled = True
extensions_in = ['.scss']
extension_out = '.css'

css = scss.Scss()


def render(path, settings):
    source = get_source(path)
    content = css.compile(source)
    return content, extension_out

