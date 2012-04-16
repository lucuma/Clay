    # -*- coding: utf-8 -*-
"""
    # Clay.p_markdown

    Text-to-HTML conversion tool for web writers

    http://daringfireball.net/projects/markdown/

"""
import os
import re

from jinja2.ext import Extension
try:
    import misaka as m
    enabled = True
except ImportError:
    enabled = False


extensions_in = ('.html.md', '.md', '.markdown',)
extension_out = '.html'

MISAKA_EXTENSIONS = m.EXT_AUTOLINK | m.EXT_TABLES | m.EXT_FENCED_CODE
MISAKA_EXTENSIONS |= m.EXT_NO_INTRA_EMPHASIS | m.EXT_STRIKETHROUGH
MISAKA_EXTENSIONS |= m.EXT_SUPERSCRIPT

MISAKA_RENDER_FLAGS =  m.HTML_TOC

RX_META = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
RX_META_MORE = re.compile(r'^[ ]{4,}(?P<value>.*)')
RX_FIRST_TITLE = re.compile(r'^\s*#\s*(?P<value>.*)\n')


def get_metadata(source):
    lines = source.split('\n')
    meta = {}
    key = None

    while True:
        if not lines:
            break # EOF
        line = lines.pop(0)
        
        if line.strip() == '':
            break # blank line - done
        
        m1 = RX_META.match(line)
        if m1:
            key = m1.group('key').lower().strip()
            value = m1.group('value').strip()
            try:
                meta[key].append(value)
            except KeyError:
                meta[key] = [value]
        else:
            m2 = RX_META_MORE.match(line)
            if m2 and key:
                # Add another line to existing key
                meta[key].append(m2.group('value').strip())
            else:
                lines.insert(0, line)
                break # no meta data - done
    
    # Flatten single items lists
    for k, v in meta.items():
        if len(v) == 1:
            meta[k] = v[0]
    
    source = '\n'.join(lines)
    return source, meta


def find_first_title(source):
    first_title = ''
    m = re.search(RX_FIRST_TITLE, source)
    if m:
        first_title = m.group(1)
    return first_title


def add_extensions(clay):

    class MarkdownExtension(Extension):

        def preprocess(self, source, name, filename=None):
            if name is None or os.path.splitext(name)[1] not in extensions_in:
                return source
            
            source, metadata = get_metadata(source)
            source = source.encode('utf-8')

            html = m.html(source, extensions=MISAKA_EXTENSIONS,
                render_flags=MISAKA_RENDER_FLAGS)
            html = unicode(html, 'utf-8')

            template = metadata.pop('template', None)

            if template:
                # Using this you can have multiple themes (HTML, epub, etc.)!
                template = clay.settings.theme_prefix + template

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

                toc_page = m.html(source, render_flags=m.HTML_TOC_TREE)
                toc_page = unicode(toc_page, 'utf-8')
                content.extend([
                    '{% block content %}', html, '{% endblock %}\n',
                    '{% block toc_page %}', toc_page, '{% endblock %}\n',
                ])
            else:
                content = [
                    '{% set ' + key + " = '''" + value + "''' %}\n"
                    for key, value in metadata.items()
                ]
                content.append(html)
            
            return ''.join(content)


    clay.render.add_extension(MarkdownExtension)

