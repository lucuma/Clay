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

JSON_COMMENTS = ('/', '#')


@manager.command
def new(new_app_path):
    """DIR_PATH

    Creates a new project
    """
    new_app_path = new_app_path.rstrip(os.path.sep)
    voodoo.reanimate_skeleton(SKELETON, new_app_path)

    print SKELETON_HELP % {'new_app_path': new_app_path}


@manager.command
def build(cwd=None):
    """.

    Generates a static version of the site
    """
    proto = get_current(cwd)
    proto.build()


@manager.command
def run(cwd=None):
    """.

    Run the development server
    """
    proto = get_current(cwd)
    proto.run()


@manager.command
def version():
    """.

    Prints the current Clay version
    """
    import clay
    print clay.__version__

#------------------------------------------------------------------------------

def get_current(cwd=None):
    cwd = '.' if cwd is None else cwd
    cwd = os.path.abspath(cwd)
    # print cwd
    settings = get_settings(cwd)
    proto = Clay(cwd, settings)
    return proto


def get_settings(cwd, filename='settings.yml'):
    settings = {}
    settings_filepath = os.path.join(cwd, filename)
    if os.path.isfile(settings_filepath):
        with io.open(settings_filepath) as f:
            source = f.read()
        settings = yaml.load(source)
    else:
        settings_filepath = os.path.join(cwd, 'settings.json')
        if os.path.isfile(settings_filepath):
            with io.open(settings_filepath) as f:
                settings_json = ''.join([l for l in f.readlines()
                    if not l.strip().startswith(JSON_COMMENTS)])
            try:
                settings = json.loads(settings_json)
            except (ValueError, SyntaxError):
                settings = {}
    return settings


def main():
    manager.run()
    print '\n'


if __name__ == "__main__":
    main()

