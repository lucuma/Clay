# coding=utf-8
"""
Fenced Code Extension for Markdown
===================================

    >>> import markdown
    >>> text = '''
    ... A paragraph before a fenced code block:
    ...
    ... ```
    ... Fenced code block
    ... ```
    ... '''
    >>> html = markdown.markdown(text, extensions=['fenced_code'])
    >>> print html
    <p>A paragraph before a fenced code block:</p>
    <pre><code>Fenced code block
    </code></pre>

Language tags:

    >>> text = '''
    ... ```python
    ... # Some python code
    ... ```'''
    >>> print markdown.markdown(text, extensions=['fenced_code'])
    <pre><code class="language-python"># Some python code
    </code></pre>

Optionally tildes instead of  backticks:

    >>> text = '''
    ... ~~~
    ... # Arbitrary code
    ... ``` # these backticks will not close the block
    ... ~~~
    >>> print markdown.markdown(text, extensions=['fenced_code'])
    <pre><code># Arbitrary code
    ``` # these backticks will not close the block
    </code></pre>


Adapted under the BSD License from the `fenced_code` and `codehilite`
extensions (Copyright 2007-2008 Waylan Limberg http://achinghead.com/).

"""
import re

from markdown import Extension
from markdown.preprocessors import Preprocessor
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter


FENCED_BLOCK_RE = re.compile(
    (r'(?P<fence>^(?:~{3,}|`{3,}))[ ]*'
     r'(?P<lang>[a-z0-9_+-]*)(?P<linenums>#)?[ ]*\n'
     r'(?P<code>.*?)'
     r'(?<=\n)(?P=fence)[ ]*$'),
    re.MULTILINE | re.DOTALL | re.IGNORECASE
)
OPEN_CODE = u'<pre><code%s>{%% raw %%}'
LANG_TAG = u' class="language-%s"'
CLOSE_CODE = '{% endraw %}</code></pre>'
TAB_LENGTH = 4


def highlight_syntax(src, lang, linenums=False):
    """Pass code to the [Pygments](http://pygments.pocoo.org/) highliter
    with optional line numbers. The output should then be styled with CSS
    to  your liking. No styles are applied by default - only styling hooks
    (i.e.: <span class="k">).
    """
    src = src.strip('\n')
    if not lang:
        lexer = TextLexer()
    else:
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ValueError:
            lexer = TextLexer()
    formatter = HtmlFormatter(linenos=linenums, tab_length=TAB_LENGTH)
    html = highlight(src, lexer, formatter)

    if lang:
        open_code = OPEN_CODE % (LANG_TAG % (lang, ), )
    else:
        open_code = OPEN_CODE % u''
    html = html.replace('<div class="highlight"><pre>', open_code, 1)
    html = html.replace('</pre></div>', CLOSE_CODE)
    return html


class FencedBlockPreprocessor(Preprocessor):

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash.
        """
        text = "\n".join(lines)
        while 1:
            m = FENCED_BLOCK_RE.search(text)
            if not m:
                break
            lang = m.group('lang')
            linenums = bool(m.group('linenums'))
            html = highlight_syntax(m.group('code'), lang, linenums=linenums)
            placeholder = self.markdown.htmlStash.store(html, safe=True)
            text = '{}\n{}\n{}'.format(
                text[:m.start()],
                placeholder,
                text[m.end():]
            )

        return text.split("\n")


class FencedCodeExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add(
            'fenced_code_block',
            FencedBlockPreprocessor(md),
            ">normalize_whitespace"
        )
