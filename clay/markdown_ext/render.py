# -*- coding: utf-8 -*-
import re

import markdown as m
from markupsafe import Markup

from .md_admonition import AdmonitionExtension
from .md_captions import FigcaptionExtension
from .md_delinsmark import DelInsMarkExtension
from .md_fencedcode import FencedCodeExtension
from .md_superscript import SuperscriptExtension


TMPL_LAYOUT = u'{{% extends "{tmpl}" %}}'


md = m.Markdown(
    extensions=[
        'meta',
        'abbr', 'attr_list', 'def_list',
        'footnotes', 'smart_strong', 'tables',
        'headerid', 'nl2br', 'sane_lists',
        AdmonitionExtension(),
        FigcaptionExtension(),
        FencedCodeExtension(),
        DelInsMarkExtension(),
        SuperscriptExtension(),
    ],
    output_format='html5',
    smart_emphasis=True,
    lazy_ol=True
)


# match all the urls
# this returns a tuple with two groups
# if the url is part of an existing link, the second element
# in the tuple will be "> or </a>
# if not, the second element will be an empty string
URL_RE = re.compile(
    r'\(?' +
    '(%s)' % '|'.join([
        r'\b[a-zA-Z]{3,7}://[^)<>\s]+[^.,)<>\s]',
        r'\b(?:www|WWW)\.[^)<>\s]+[^.,)<>\s]',
    ])
    + r'(">|</a>)?'
)


def autolink(html):
    urls = URL_RE.findall(html)
    for m_url in urls:
        # ignore urls that are part of a link already
        if m_url[1]:
            continue
        url = m_url[0]
        text = url

        # ignore parens if they enclose the entire url
        if url[0] == '(' and url[-1] == ')':
            url = url[1:-1]

        protocol = url.split('://')[0]
        if not protocol or protocol == url:
            url = 'http://' + url

        # substitute only where the url is not already part of a
        # link element.
        html = re.sub('(?<!(="|">))' + re.escape(text),
                      '<a href="' + url + '">' + text + '</a>',
                      html)
    return html


BLOCK_OPEN_RE = re.compile(r'({[{%])(%20)+')
BLOCK_CLOSE_RE = re.compile(r'(%20)+([%}]})')


def md_to_jinja(source):
    md.reset()
    tmpl = []
    html = md.convert(source)
    html = re.sub(BLOCK_OPEN_RE, '\g<1> ', html)
    html = re.sub(BLOCK_CLOSE_RE, ' \g<2>', html)
    html = autolink(html)
    layout = md.Meta.pop('layout', None)
    if layout:
        layout_fragment = TMPL_LAYOUT.format(tmpl=layout[0])
        tmpl.append(layout_fragment)
    else:
        tmpl.append(html)

    meta = dict((name, Markup(value[0])) for name, value in md.Meta.items())
    meta['content'] = Markup(html)
    _source = '\n'.join(tmpl)
    return _source, meta
