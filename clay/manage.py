#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Clay.manage

Command line scripts.

"""
import io
import os
import sys

from shake import manager, json
import voodoo
import yaml

from .config import SOURCE_DIR
from .core import Clay


WELCOME = """
\033[1m Clay \033[0m - A rapid prototyping tool by Lucuma labs"""

SKELETON = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    'skeleton')

SKELETON_HELP = """
    Done!
    Now go to %(new_app_path)s, and run `clay run` to start the server.
    Don't forget to read the README.md
    """

SOURCE_NOT_FOUND_HELP = """We couldn't found a source dir ('%s' or 'views').
Are you sure you're in the correct folder?
""" % SOURCE_DIR


class SourceDirNotFound(Exception):
    pass


@manager.command
def new(new_app_path='.'):
    """DIR_PATH

    Creates a new project
    """
    new_app_path = new_app_path.rstrip(os.path.sep)
    voodoo.reanimate_skeleton(SKELETON, new_app_path)

    print SKELETON_HELP % {'new_app_path': new_app_path}


@manager.command
def build(theme_prefix=''):
    """.

    Generates a static version of the site
    """
    try:
        proto = get_current(theme_prefix)
    except SourceDirNotFound:
        print SOURCE_NOT_FOUND_HELP
        return
    proto.build()


@manager.command
def run(theme_prefix=''):
    """.

    Run the development server
    """
    try:
        proto = get_current(theme_prefix)
    except SourceDirNotFound:
        print SOURCE_NOT_FOUND_HELP
        return
    proto.run()


@manager.command
def version():
    """.

    Prints the current Clay version
    """
    import clay
    print clay.__version__

#------------------------------------------------------------------------------

def get_current(theme_prefix='', cwd=None):
    cwd = '.' if cwd is None else cwd
    cwd = os.path.abspath(cwd)
    # print cwd
    source_dir = get_source_dir(cwd)
    settings = get_settings(cwd)
    settings.setdefault('theme_prefix', theme_prefix)
    
    return Clay(cwd, settings, source_dir=source_dir)


def get_source_dir(cwd):
    sources = [SOURCE_DIR, 'views']
    for source in sources:
        if os.path.exists(os.path.join(cwd, source)):
            return source
    raise SourceDirNotFound


def get_settings(cwd, filename='settings.yml'):
    settings = {}
    settings_filepath = os.path.join(cwd, filename)
    if os.path.isfile(settings_filepath):
        with io.open(settings_filepath) as f:
            source = f.read()
        settings = yaml.load(source)

    return settings


def main():
    manager.run()
    print '\n'


if __name__ == "__main__":
    main()

