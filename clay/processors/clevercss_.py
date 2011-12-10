# -*- coding: utf-8 -*-
"""
    # Clay.processors.clevercss

    http://sandbox.pocoo.org/clevercss/

"""
from ..libs import clevercss
from ..utils import get_source


enabled = True
extensions_in = ['.css.ccss', '.ccss']
extension_out = '.css'


def render(path, settings):
    source = get_source(path)
    content = clevercss.convert(source)
    return content, extension_out

