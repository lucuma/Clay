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

extensions_in = ['.coffee']
# This is for servers/browsers so 'application/javascript' doesn't work
mimetype_out = 'text/javascript'
extension_out = 'js'


def parse_settings(args, settings):
    bare = settings.get('bare', False)
    if bare:
        args.append('--bare')


def render(filepath_in, settings):
    fn, ext = os.path.splitext(filepath_in)
    filepath_out = '.'.join([fn, extension_out])
    args = [COMMAND, '--compile', filepath_in]
    parse_settings(args, settings)
    subprocess.call(args)
    return get_source(filepath_out)


def build(filepath_in, filepath_out, settings):
    args = [COMMAND, '--compile', filepath_in]
    parse_settings(args, settings)
    subprocess.call(args)

