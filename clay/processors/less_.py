# -*- coding: utf-8 -*-
"""
    # Clay.processors.less

    http://lesscss.org/

"""
import io
import subprocess


COMMAND = 'lessc'

try:
    subprocess.check_output([COMMAND, '--version'])
    enabled = True
except OSError:
    enabled = False

extensions_in = ['.css.less', '.less']
extension_out = '.css'


def render(path, settings):
    content = subprocess.check_output([COMMAND, path])
    return content, extension_out

