# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from os.path import dirname
import re

from flask import request
from jinja2.ext import Extension


def _norm_url(url):
    url = url.rstrip('/')
    if url.startswith('/'):
        return url
    baseurl = dirname(request.path.strip('/'))
    if baseurl:
        return '/' + '/'.join([baseurl, url])
    return '/' + url


def active(*url_patterns, **kwargs):
    partial = kwargs.get('partial')

    path = request.path.rstrip('/')
    resp = u''
    # for backward compatibility
    if len(url_patterns) == 1 and isinstance(url_patterns[0], (list, tuple)):
        url_patterns = url_patterns[0]
    #
    for url in url_patterns:
        url = _norm_url(url)
        if fnmatch(path, url) or (partial and path.startswith(url)):
            return 'active'
    return resp


class IncludeWith(Extension):
    """A Jinja2 preprocessor extension that let you update the `include`
    context like this:

        {% include "something.html" with foo=bar %}
        {% include "something.html" with a=3, b=2+2, c='yes' %}

    You **must** also include 'jinja2.ext.with_' in the extensions list.
    """

    rx = re.compile(r'\{\%\s*include\s+(?P<tmpl>[^\s]+)\s+with\s+'
                    '(?P<context>.*?)\s*\%\}', re.IGNORECASE)

    def preprocess(self, source, name, filename=None):
        lastpos = 0
        while 1:
            m = self.rx.search(source, lastpos)
            if not m:
                break

            lastpos = m.end()
            d = m.groupdict()
            context = d['context'].strip()
            if context == 'context':
                continue

            source = ''.join([
                source[:m.start()],
                '{% with ', context, ' %}',
                '{% include ', d['tmpl'].strip(), ' %}',
                '{% endwith %}',
                source[m.end():]
            ])

        return source
