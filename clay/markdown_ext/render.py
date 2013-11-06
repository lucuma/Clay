# -*- coding: utf-8 -*-
import markdown as m
import re

from .md_admonition import AdmonitionExtension
from .md_delinsmark import DelInsMarkExtension
from .md_fencedcode import FencedCodeExtension
from .md_superscript import SuperscriptExtension


TMPL_LAYOUT = u'{%% extends "%s" %%}'
TMPL_BLOCK = u'{%% block %s %%}%s{%% endblock %%}'


md = m.Markdown(
    extensions=['meta',
        AdmonitionExtension(), FencedCodeExtension(),
        DelInsMarkExtension(), SuperscriptExtension(),
        'abbr', 'attr_list', 'def_list', 'footnotes', 'smart_strong',
        'tables', 'headerid', 'nl2br', 'sane_lists',
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


def md_to_jinja(source):
    md.reset()
    tmpl = []
    html = md.convert(source)
    html = autolink(html)
    layout = md.Meta.pop('layout', None)
    if layout:
        tmpl.append(TMPL_LAYOUT % (layout[0], ))

    for name, value in md.Meta.items():
        tmpl.append(TMPL_BLOCK % (name, value[0]))

    tmpl.append(TMPL_BLOCK % (u'content', html))
    return '\n'.join(tmpl)
