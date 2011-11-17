# -*- coding: utf-8 -*-
import io
import os

from clay.manage import new, make, run, get_settings, get_current
import pytest
# from shake import execute


def get_cwd():
    return os.path.dirname(os.path.abspath(__file__)) or '.'


def test_get_settings():
    cwd = get_cwd()
    settings = get_settings(cwd, filename='_test.json')

    assert settings
    assert 'views_list' in settings


def test_get_current():
    expected = os.getcwd()
    proto = get_current()
    
    assert proto.base_dir == expected


# def test_make():
#     cwd = get_cwd()
#     build_dir = os.path.join(cwd, 'build')
#     try:
#         os.remove(build_dir)
#     except OSError:
#         pass
    
#     execute('clay', ['make', cwd])
    
#     assert os.path.isdir(build_dir)

