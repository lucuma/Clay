# -*- coding: utf-8 -*-
"""
# Clay.processors.clevercss

http://sandbox.pocoo.org/clevercss/
"""
try:
    import clevercss
    enabled = True
except ImportError:
    enabled = False

from ..utils import get_source, make_file


extensions_in = ['.ccss']
mimetype_out = 'text/css'
extension_out = 'css'


def render(filepath_in):
    source = get_source(filepath_in)
    return clevercss.convert(source)


def make(filepath_in, filepath_out):
    content = render(filepath_in)
    make_file(filepath_out, content)

