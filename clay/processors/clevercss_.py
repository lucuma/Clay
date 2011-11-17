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


extensions_in = ['.ccss']

mimetype_out = 'text/css'
extension_out = 'css'


def convert(source):
    return clevercss.convert(source)

