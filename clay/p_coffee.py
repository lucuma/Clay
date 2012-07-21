# -*- coding: utf-8 -*-
"""
    # Clay.p_coffee

    http://jashkenas.github.com/coffee-script/

"""
import os
import subprocess

from jinja2.ext import Extension

from .utils import get_source, remove_file


COMMAND = 'coffee'

try:
    subprocess.check_output([COMMAND, '--version'])
    enabled = True
except Exception:
    enabled = False

extensions_in = ('.js.coffee',  '.coffee',)
extension_out = '.js'


def add_extensions(clay):

    class CoffeeExtension(Extension):

        def preprocess(self, source, name, filename=None):
            if name is None or os.path.splitext(name)[1] not in extensions_in:
                return source
            
            path = os.path.join(clay.source_dir, name)
            fn, ext = os.path.splitext(path)
            filepath_out = fn + extension_out
            try:
                args = [COMMAND, '--compile', path]
                subprocess.call(args)
                content = get_source(filepath_out)
            except subprocess.CalledProcessError:
                content = ''
            finally:
                remove_file(filepath_out)
            return content

    clay.render.env.add_extension(CoffeeExtension)

