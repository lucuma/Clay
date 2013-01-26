# -*- coding: utf-8 -*-
from __future__ import print_function

from os.path import dirname, join, realpath, sep, abspath

from pyceo import Manager
from voodoo import reanimate_skeleton

from .main import Clay, DEFAULT_HOST, DEFAULT_PORT


manager = Manager()

SKELETON = join(dirname(realpath(__file__)), 'skeleton')

SKELETON_HELP = """
    Done!
    Now go to %s, and do `clay run` to start the server.
"""


@manager.command
def new(path='.'):
    """[path='.']
    Creates a new project
    """
    path = abspath(path.rstrip(sep))
    reanimate_skeleton(SKELETON, path)
    print(SKELETON_HELP % (path,))


@manager.command
def run(host=DEFAULT_HOST, port=DEFAULT_PORT, path='.'):
    """[host] [port] [path='.']
    Run the development server
    """
    path = abspath(path)
    c = Clay(path)
    c.run(host=host, port=port)


@manager.command
def build(path='.'):
    """[path='.']
    Generates a static copy of the sources
    """
    path = abspath(path)
    c = Clay(path)
    c.build()


@manager.command
def version():
    """.
    Returns the current Clay version
    """
    from . import __version__
    print(__version__)


def main():
    manager.run()

