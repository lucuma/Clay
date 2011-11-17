#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import sys

from shake import manager, json
import voodoo

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
def make(cwd=None):
    """
    Generates a static version of the site
    """
    proto = get_current(cwd)
    proto.make()


@manager.command
def build(cwd=None):
    """
    An alias for 'clay make'
    """
    return make(cwd)


@manager.command
def run(cwd=None):
    """
    Run the development server
    """
    proto = get_current(cwd)
    proto.run()


def get_current(cwd=None):
    cwd = '.' if cwd is None else cwd
    cwd = os.path.abspath(cwd)
    # print cwd
    settings = get_settings(cwd)
    proto = Clay(cwd, settings)
    return proto


def get_settings(cwd, filename='settings.json'):
    settings = {}
    settings_filepath = os.path.join(cwd, filename)
    if os.path.isfile(settings_filepath):
        with io.open(settings_filepath) as f:
            settings_json = ''.join([l for l in f.readlines()
                if not l.strip().startswith(JSON_COMMENTS)])
        try:
            settings = json.loads(settings_json)
        except ValueError:
            settings = {}
    return settings


def main():
    manager.run(prefix=WELCOME)


if __name__ == "__main__":
    main()

