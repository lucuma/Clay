# -*- coding: utf-8 -*-
"""
    # Clay.processors.markdown_jinja

    A markdown pre-compiler for jinja templates.
    http://www.freewisdom.org/projects/python-markdown/

"""
import os
from string import Template

from jinja2.ext import Extension
import markdown


extensions_in = ['.md', '.markdown']

WRAPPER = Template("""{% extends "$base" %}

{% block title %}$title{% endblock %}

{% block content %}
$_html
{% endblock %}
""")


def get_extension(settings):

    md = markdown.Markdown(
        extensions=settings.markdown_extensions,
        safe_mode=settings.markdown_safe_mode,
        output_format=settings.markdown_output_format
    )

    class MarkdownExtension(Extension):
        
        def preprocess(self, source, name, filename=None):
            if not os.path.splitext(name)[1] in extensions_in:
                return source
            
            html = md.convert(source)
            meta = md.Meta
            data = {}
            data['title'] = meta.get('title', [u''])[0].strip()
            data['base'] = meta.get('base', [u'base.html'])[0].strip()
            data['_html'] = html

            return WRAPPER.substitute(data)
    
    return MarkdownExtension

