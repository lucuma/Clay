# -*- coding: utf-8 -*-
import io
import os

from clay.manage import new, make, run, get_settings
import pytest
from shake import execute


def test_get_settings():
    cwd = os.path.dirname(os.path.realpath(__file__))
    settings = get_settings(cwd, filename='_test.json')

    assert settings
    assert 'views_list' in settings


def test_make():
    cwd = os.path.dirname(os.path.realpath(__file__))
    build_dir = os.path.join(cwd, 'build')
    try:
        os.remove(build_dir)
    except OSError:
        pass
    
    execute('clay', 'make')

    assert os.path.isdir(build_dir)
