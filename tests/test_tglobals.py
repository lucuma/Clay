# -*- coding: utf-8 -*-
from __future__ import absolute_import

from clay.tglobals import link_to

from .helpers import *


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

