# -*- coding: utf-8 -*-
"""
# Clay.processors.clevercss

http://sandbox.pocoo.org/clevercss/

"""
from ..libs import clevercss
from ..utils import get_source, make_file


enabled = True

extensions_in = ['.ccss']
mimetype_out = 'text/css'
extension_out = 'css'


def render(filepath_in, settings):
    source = get_source(filepath_in)
    return clevercss.convert(source)


def build(filepath_in, filepath_out, settings):
    content = render(filepath_in, settings)
    make_file(filepath_out, content)

