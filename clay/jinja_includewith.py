# -*- coding: utf-8 -*-
"""
    Jinja2IncludeWith
    ~~~~~~~~~~~~~~~~~~

    A Jinja2 preprocessor extension that let you update the `include`
    context like this:

        {% include "something.html" with foo=bar %}
        {% include "something.html" with a=3, b=2+2, c='yes' %}

    You **must** also include 'jinja2.ext.with_' in the extensions list.

    :copyright: (c) 2012 by Juan-Pablo Scaletti.
    :license: MIT, see LICENSE for more details.
"""
import re

from jinja2.ext import Extension


__version__ = '0.1'

rx = re.compile(r'\{\%\s*include\s+(?P<tmpl>[^\s]+)\s+with\s+(?P<context>(?:[a-z0-9_-]+\s*=\s*[^%,]+)(?:\s*,\s*[a-z0-9_-]+\s*=\s*[^%,]+)*)\s*\%\}', re.IGNORECASE)


class IncludeWith(Extension):

    def preprocess(self, source, name, filename=None):
        blocks =  rx.finditer(source)
        for m in blocks:
            d = m.groupdict()
            d['context'] = d['context'].strip()

            source = ''.join([
                source[:m.start()],
                '{% with ', d['context'].strip(), '%}',
                '{% include ', d['tmpl'].strip(), ' %}',
                '{% endwith %}',
                source[m.end():]
                ])
        return source

