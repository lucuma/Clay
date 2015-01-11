# -*- coding: utf-8 -*-
from collections import OrderedDict
from fnmatch import fnmatch
from functools import partial
import os
from os.path import dirname, abspath, isdir, isfile, join
import re

from flask import request

from .helpers import to_unicode


def norm_url(url):
    url = url.strip().rstrip('/')
    url = re.sub('index.html$', '', url).rstrip('/')
    if url.startswith('/'):
        return url
    baseurl = dirname(request.path.strip('/'))
    if baseurl:
        return '/' + '/'.join([baseurl, url])
    return '/' + url


def active(*url_patterns, **kwargs):
    partial = kwargs.get('partial')

    path = norm_url(request.path)

    # Accept single patterns also
    if len(url_patterns) == 1 and isinstance(url_patterns[0], (list, tuple)):
        url_patterns = url_patterns[0]

    for urlp in url_patterns:
        urlp = norm_url(urlp)
        if fnmatch(path, urlp) or (partial and path.startswith(urlp)):
            return 'active'
    return u''


class ToC(object):
    """Recursevly builds a tree of (name, relpath) of all files and subfolders
    of a given path.

    Usage:

        clay
        ├── __init__.py
        ├── helpers.py
        ├── main.py
        └── source
            ├── _index.html
            ├── _index.txt
            └── foo
                └── bar.html


        >>> toc = TOC('/Users/bla/Projects/clay/clay')
        >>> list(toc)
        [
            (u'__init__.py', u'/__init__.py'),
            (u'helpers.py', u'/helpers.py'),
            (u'main.py', u'/main.py'),
        ]
        >>> list(toc.source)
        [
            (u'_index.html', u'/source/_index.html'),
            (u'_index.txt', u'/source/_index.txt'),
            (u'_notfound.html', u'/source/_notfound.html'),
        ]
        >>> toc(maxdepth=1)
        '''<ul class="toc">
            <li><a href="/__init__.py">__init__.py</a></li>
            <li><a href="/helpers.py">helpers.py</a></li>
            <li><a href="/main.py">main.py</a></li>
            <li><span>source</span>
                <ul>
                    <li><a href="/source/_index.html">_index</a></li>
                    <li><a href="/source/_index.txt">_index.txt</a></li>
                </ul>
            </li>
        </ul>'''
        >>> toc.source(maxdepth=1)
        '''<ul class="toc">
            <li><a href="/source/_index.html">_index</a></li>
            <li><a href="/source/_index.txt">_index.txt</a></li>
            <li><span>foo</span>
                <ul>
                    <li><a href="/source/foo/bar.html">bar.html</a></li>
                </ul>
            </li>
        </ul>'''
        >>> toc(maxdepth=1, folders_first=True)
        '''<ul class="toc">
            <li><span>source</span>
                <ul class="toc">
                    <li><a href="/source/_index.html">_index</a></li>
                    <li><a href="/source/_index.txt">_index.txt</a></li>
                </ul>
            </li>
            <li><a href="/__init__.py">__init__.py</a></li>
            <li><a href="/helpers.py">helpers.py</a></li>
            <li><a href="/main.py">main.py</a></li>
        </ul>'''

    """
    def __init__(self, basepath, baseurl='/', filter=('.*', '*.pyc')):
        self._leafs = []
        self._branches = []
        basepath = abspath(to_unicode(basepath))
        if isdir(basepath):
            self.__buildtree(basepath, baseurl, filter)

    def __buildtree(self, basepath, baseurl, filter):
        leafs = OrderedDict()
        branches = OrderedDict()

        names = sorted(os.listdir(basepath))
        for name in names:
            if any(map(partial(fnmatch, name), filter)):
                continue
            if isfile(join(basepath, name)):
                leafs[name] = join(baseurl, name)
            else:
                new_basepath = join(basepath, name)
                new_baseurl = join(baseurl, name)
                branches[name] = ToC(new_basepath, baseurl=new_baseurl)

        self._leafs = leafs
        self._branches = branches

    def __getattr__(self, name):
        node = self._leafs.get(name)
        if not node:
            node = self._branches.get(name)
            if not node:
                raise AttributeError
        return node

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __iter__(self):
        return self._leafs.iteritems()

    def __call__(self, maxdepth=1, folders_first=False, indent=4, _depth=0):
        html_leafs = self._render_leafs(
            indent=indent,
            _depth=_depth
        )
        html_branches = u''
        if maxdepth:
            html_branches = self._render_branches(
                maxdepth=(maxdepth - 1),
                folders_first=folders_first,
                indent=indent,
                _depth=_depth
            )
        tmpl = u'{indent}<ul class="toc">\n{html1}{html2}{indent}</ul>'
        if folders_first:
            html1 = html_branches
            html2 = html_leafs
        else:
            html1 = html_leafs
            html2 = html_branches
        return tmpl.format(
            html1=html1,
            html2=html2,
            indent=u' ' * (indent * _depth)
        )

    def _render_leafs(self, indent, _depth):
        lis = []
        _indent = u' ' * (indent * (_depth + 1))

        for name, path in self._leafs.items():
            html = u'{indent}<li><a href="{path}">{name}</a></li>'.format(
                indent=_indent, name=name, path=path
            )
            lis.append(html)

        if not lis:
            return u''
        return u'\n'.join(lis) + u'\n'

    def _render_branches(self, maxdepth, folders_first, indent, _depth):
        uls = []
        for name, toc in self._branches.items():
            tmpl = u'{indent}<li><span>{name}</span>\n{subtoc}\n{indent}</li>'
            ulhtml = tmpl.format(
                name=name,
                indent=u' ' * (indent * (_depth + 1)),
                subtoc=toc(
                    maxdepth=maxdepth - 1,
                    folders_first=folders_first,
                    indent=indent,
                    _depth=_depth + 2
                )
            )
            uls.append(ulhtml)

        if not uls:
            return u''
        return u'\n'.join(uls) + u'\n'
