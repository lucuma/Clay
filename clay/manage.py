#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import sys

from shake import manager, json
import voodoo

from .core import Clay


SKELETON = os.path.join(os.path.dirname(os.path.realpath(__file__)),
    'skeleton')

SKELETON_HELP = """
    Done!
    Now go to %(new_app_path)s, and run `python run.py` to start the server.
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
    """DIR_PATH

    Generates a static version of the site
    """
    clay = get_current(cwd)
    clay.make()


@manager.command
def run(cwd=None):
    """DIR_PATH

    Run the development server
    """
    clay = get_current(cwd)
    clay.run()


def get_current(cwd=None):
    cwd = os.getcwd() if cwd is None else cwd
    cwd = os.path.dirname(os.path.realpath(cwd))
    settings = get_settings(cwd)
    clay = Clay(cwd, settings)
    return clay


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
    manager.run()


if __name__ == "__main__":
    manager.run(default='run')

