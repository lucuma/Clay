# -*- coding: utf-8 -*-
"""
    # Clay.p_scss

    Sassy CSS processor

    http://sass-lang.com/
    https://github.com/Kronuz/pyScss

"""
import os

from jinja2.ext import Extension
try:
    import scss
    enabled = True
except ImportError:
    enabled = False


extensions_in = ('.css.scss', '.scss',)
extension_out = '.css'


def add_extensions(clay):
    css = scss.Scss()

    class SassyCSSExtension(Extension):

        def preprocess(self, source, name, filename=None):
            if name is None or os.path.splitext(name)[1] not in extensions_in:
                return source
            return css.compile(source)
    
    clay.render.env.add_extension(SassyCSSExtension)

