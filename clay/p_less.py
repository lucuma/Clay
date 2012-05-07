# -*- coding: utf-8 -*-
"""
    # Clay.p_less

    http://lesscss.org/

"""
import os
import subprocess

from jinja2.ext import Extension


COMMAND = 'lessc'

try:
    subprocess.check_output([COMMAND, '--version'])
    enabled = True
except Exception:
    enabled = False

extensions_in = ('.css.less', '.less',)
extension_out = '.css'


def add_extensions(clay):

    class LessExtension(Extension):

        def preprocess(self, source, name, filename=None):
            if name is None or os.path.splitext(name)[1] not in extensions_in:
                return source
            path = os.path.join(clay.source_dir, name)
            try:
                content = subprocess.check_output([COMMAND, path])
            except subprocess.CalledProcessError:
                # Import error?
                content = ''
            return content

    clay.render.add_extension(LessExtension)

