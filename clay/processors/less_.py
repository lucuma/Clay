# -*- coding: utf-8 -*-
"""
# Clay.processors.less

http://lesscss.org/
"""
import io
import subprocess


COMMAND = 'lessc'

try:
    subprocess.check_call([COMMAND, '--version'])
    enabled = True
except OSError:
    enabled = False

extensions_in = ['.less']
mimetype_out = 'text/css'
extension_out = 'css'


def render(filepath_in):
    return subprocess.check_output([COMMAND, filepath_in])


def make(filepath_in, filepath_out):
    try:
        stdout = io.open(filepath_out)
        subprocess.check_output([COMMAND, filepath_in], stdout=stdout)
    finally:
        stdout.close()

