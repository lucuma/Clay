# -*- coding: utf-8 -*-
from clay.tglobals import active

from .helpers import *


def setup_module():
    remove_test_dirs()
    make_dirs(SOURCE_DIR)


def teardown_module():
    remove_test_dirs()


def _test_active_case(path, as_expected, partial=False):
    html = active(path, partial=partial)
    assert (html == 'active') is as_expected


def _test_active(path):
    _test_active_case('/hello/', False)
    _test_active_case(path, True)
    _test_active_case('/foo/', True, partial=True)
    _test_active_case(['/hello/', path], True)
    _test_active_case(['/hello/', '/world/'], False)


def test_active(c):
    path = '/foo/bar/'
    with c.app.test_request_context(path, method='GET'):
        _test_active(path)


def test_active_in_templates(t):
    setup_module()
    make_dirs(SOURCE_DIR)

    path = 'bbbb.html'
    content = u'''class="{{ active('%s') }}"''' % path
    create_file(get_source_path(path), content)

    expected = u'class="active"'
    resp = t.get('/' + path)
    assert resp.data == expected

