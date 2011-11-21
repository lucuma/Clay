# -*- coding: utf-8 -*-
"""
# Clay.processors.scss

Sassy CSS processor

http://sass-lang.com/
https://github.com/Kronuz/pyScss
"""
from ..libs import scss
from ..utils import get_source, make_file


enabled = True

extensions_in = ['.scss']
mimetype_out = 'text/css'
extension_out = 'css'

css = scss.Scss()


def render(filepath_in, settings):
    source = get_source(filepath_in)
    return css.compile(source)


def build(filepath_in, filepath_out, settings):
    content = render(filepath_in, settings)
    make_file(filepath_out, content)

