# coding=utf-8
import re
from jinja2.ext import Extension


class IncludeWith(Extension):
    """A Jinja2 preprocessor extension that let you update the `include`
    context like this:

        {% include "something.html" with foo=bar %}
        {% include "something.html" with a=3, b=2+2, c='yes' %}

    You **must** also include 'jinja2.ext.with_' in the extensions list.
    """

    rx = re.compile(
        r'\{\%-?[\s\n]*include[\s\n]+(?P<tmpl>[^\s\n]+)[\s\n]+with[\s\n]+'
        '(?P<context>.*?)[\s\n]*-?\%\}',
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
