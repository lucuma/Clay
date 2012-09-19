# -*- coding: utf-8 -*-
import io
import os

from clay.manage import new, build, run, get_settings, get_current
import pytest


THIS_DIR = os.path.dirname(__file__)


def test_get_settings():
    settings = get_settings(THIS_DIR, filename='settings.yml')
    assert settings


def test_get_current():
    os.chdir(os.path.dirname(__file__))
    expected = os.getcwd()
    clay_ = get_current()
    assert clay_.base_dir == expected

