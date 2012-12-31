# -*- coding: utf-8 -*-
from __future__ import absolute_import

from clay.tglobals import link_to, active

from .helpers import *


def setup_module():
    remove_test_dirs()
    make_dirs(SOURCE_DIR)


def teardown_module():
    remove_test_dirs()


def _test_link_to(path):
    html = link_to(u'Hello', '/hello/', title='click me')
    expected = u'<a href="/hello/" title="click me">Hello</a>'
    assert expected == html

    html = link_to(u'Hello', '/hello/', data_update=True)
    expected = u'<a href="/hello/" data-update>Hello</a>'
    assert expected == html

    html = link_to(u'Bar', path)
    expected = u'<a href="/foo/bar/" class="active">Bar</a>'
    assert expected == html

    html = link_to(u'Bar', path, wrapper='li')
    expected = u'<li class="active"><a href="/foo/bar/">Bar</a></li>'
    assert expected == html

    html = link_to(u'Bar', path, classes='xxx yyy', wrapper='li')
    expected = u'<li class="xxx yyy active"><a href="/foo/bar/">Bar</a></li>'
    assert expected == html

    html = link_to(u'Bar', '/foo/', partial=True)
    expected = u'<a href="/foo/" class="active">Bar</a>'
    assert expected == html

    html = link_to(u'Bar', ['/hello/', path])
    expected = u'<a href="/hello/" class="active">Bar</a>'
    assert expected == html

    html = link_to('Hello', ['/hello/', '/world/'], title=u'click me')
    expected = u'<a href="/hello/" title="click me">Hello</a>'
    assert expected == html


def test_link_to(c):
    path = '/foo/bar/'
    with c.app.test_request_context(path, method='GET'):
        _test_link_to(path)


def test_link_to_in_templates(t):
    setup_module()
    make_dirs(SOURCE_DIR)

    path = 'aaaa.html'
    content = u"{{ link_to('', '%s') }}" % path
    create_file(get_source_path(path), content)

    expected = u'<a href="%s" class="active"></a>' % path
    resp = t.get('/' + path)
    assert resp.data == expected


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

