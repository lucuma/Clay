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

extensions_in = ['.less']
mimetype_out = 'text/css'
extension_out = 'css'


def render(filepath_in, settings):
    return subprocess.check_output([COMMAND, filepath_in])


def build(filepath_in, filepath_out, settings):
    stdout = io.open(filepath_out, 'w+t')
    subprocess.call([COMMAND, filepath_in], stdout=stdout)

