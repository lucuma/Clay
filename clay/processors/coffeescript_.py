# -*- coding: utf-8 -*-
"""
    # Clay.processors.coffescript

    http://jashkenas.github.com/coffee-script/

"""
import io
import os
import subprocess

from ..utils import get_source


COMMAND = 'coffee'

try:
    subprocess.check_output([COMMAND, '--version'])
    enabled = True
except OSError:
    enabled = False

extensions_in = ['.js.coffee',  '.coffee']
extension_out = '.js'


def parse_settings(args, settings):
    bare = settings.get('bare', False)
    if bare:
        args.append('--bare')


def render(path, settings):
    fn, ext = os.path.splitext(path)
    filepath_out = ''.join([fn, extension_out])
    args = [COMMAND, '--compile', path]
    parse_settings(args, settings)
    subprocess.call(args)
    content = get_source(filepath_out)
    return content, extension_out

