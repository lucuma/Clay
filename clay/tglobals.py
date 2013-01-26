# -*- coding: utf-8 -*-
import re

from flask import request
from jinja2.ext import Extension


def _norm_url(url):
    return '/' + url.strip('/')


def active(url='/', partial=False):
    path = request.path.rstrip('/')
    resp = u''
    patterns = url if isinstance(url, (list, tuple)) else [url]

    for url in patterns:
        url = _norm_url(url)
        if path == url or (partial and path.startswith(url)):
            return 'active'

    return resp


class IncludeWith(Extension):
    """A Jinja2 preprocessor extension that let you update the `include`
    context like this:

        {% include "something.html" with foo=bar %}
        {% include "something.html" with a=3, b=2+2, c='yes' %}

    You **must** also include 'jinja2.ext.with_' in the extensions list.
    """

    rx = re.compile(r'\{\%\s*include\s+(?P<tmpl>[^\s]+)\s+with\s+(?P<context>.*?)\s*\%\}',
        re.IGNORECASE)

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

