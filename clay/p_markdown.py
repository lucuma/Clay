    # -*- coding: utf-8 -*-
"""
    # Clay.p_markdown

    Text-to-HTML conversion tool for web writers

    http://daringfireball.net/projects/markdown/
    http://packages.python.org/Markdown

"""
import os
import re

from jinja2.ext import Extension
try:
    import markdown
    enabled = True
except ImportError:
    enabled = False

from .utils import to_unicode


extensions_in = ('.md', '.markdown', '.mdown', '.html.md', '.html.mdown', '.html.markdown',)
extension_out = '.html'

RX_FIRST_TITLE = re.compile(r'^\s*#\s*(?P<value>.*)\n')


def get_metadata(md):
    meta = md.Meta
    # Flatten single items lists
    for k, v in meta.items():
        if len(v) == 1:
            v = v[0]
            meta[k] = v
        if isinstance(v, basestring) and k != 'template':
            v = md.convert(v.strip()).strip()
            v = re.sub(r'^\<p\>', '', v)
            v = re.sub(r'\<\/p\>$', '', v)
            meta[k] = v
    return meta


def find_first_title(source):
    first_title = ''
    m = re.search(RX_FIRST_TITLE, source)
    if m:
        first_title = m.group(1)
    return first_title


def add_extensions(clay):
    from .libs.md_fenced_gh import FencedCodeGhExtension
    from .libs.md_superscript import SuperscriptExtension
    from .libs.md_toc import TocExtension

    md_options = {
        'extensions': [
            'meta',
            'abbr',
            'def_list',
            'footnotes',
            'nl2br',
            'smart_strong',
            'tables',
            'attr_list',
            FencedCodeGhExtension(),
            SuperscriptExtension(),
            TocExtension(),
        ],
        'output_format': 'html5',
        'safe_mode': False,
        'tab_length': 4,
        'enable_attributes': True,
        'smart_emphasis': True,
        'lazy_ol': True
    }
    md = markdown.Markdown(**md_options)
    md.preprocessors['html_block'].markdown_in_raw = True
    theme_prefix = clay.settings.get('theme_prefix', '')


    class MarkdownExtension(Extension):

        def preprocess(self, source, name, filename=None):
            if name is None or os.path.splitext(name)[1] not in extensions_in:
                return source

            source = to_unicode(source)
            html = md.convert(source)
            metadata = get_metadata(md)
            toc_page = md.toc
            md.reset()

            template = metadata.pop('template', None)

            if template:
                # Using this you can have multiple themes (HTML, epub, etc.)!
                template = theme_prefix + template

                page_title = metadata.pop('title', None)
                if not page_title:
                    page_title = find_first_title(source)

                content = [
                    '{% extends "', template, '" %}\n',
                    '{% block title %}', page_title, '{% endblock %}\n',
                ]
                content.extend([
                    '{% block ' + key + ' %}' + value + '{% endblock %}\n'
                    for key, value in metadata.items()
                ])

                content.extend([
                    '{% block content %}', html, '{% endblock %}\n',
                    '{% block toc %}', toc_page, '{% endblock %}\n',
                ])
            else:
                content = [
                    '{% set ' + key + " = '''" + value + "''' %}\n"
                    for key, value in metadata.items()
                ]
                content.append(html)
            
            return ''.join(content)

    clay.render.env.add_extension(MarkdownExtension)

