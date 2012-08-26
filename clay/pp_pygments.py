# -*- coding: utf-8 -*-
"""
    # Clay.pp_pygments

    Highlight codeblocks with Pygments by passing HTML through it.

"""
import re

try:
    import pygments
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name, ClassNotFound
    enabled = True
except ImportError:
    enabled = False


RX_CODEBLOCK = re.compile(r'<pre(?: lang="([a-z0-9]+#?)")?><code'
    '(?: class="([a-z0-9_\-]+#?).*?")?>(.*?)</code></pre>',
    re.IGNORECASE | re.DOTALL)


class CodeHtmlFormatter(HtmlFormatter):

    def wrap(self, source, outfile):
        return self._wrap_pre(self._wrap_code(source))

    def _wrap_code(self, source):
        yield 0, ('<code' + (self.cssclass and ' class="%s"' % self.cssclass)
            + '>')
        for tup in source:
            yield tup
        yield 0, '</code>'


def _unescape_html(html):
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&amp;', '&')
    html = html.replace('&quot;', '"')
    return html


def _highlight_match(match):
    language, classname, code = match.groups()
    lang_or_class = language or classname

    if lang_or_class is None:
        return match.group(0)

    linenos = False
    if lang_or_class.endswith('#'):
        lang_or_class = lang_or_class[:-1]
        linenos = True

    try:
        lexer = get_lexer_by_name(lang_or_class)
    except ClassNotFound:
        return match.group(0)
    
    formatter = CodeHtmlFormatter(
        cssclass='highlight ' + lang_or_class,
        linenos=linenos
    )

    return highlight(_unescape_html(code), lexer, formatter)


def process(html):
    return RX_CODEBLOCK.sub(_highlight_match, html)

