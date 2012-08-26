# -*- coding: utf-8 -*-
"""
# Fenced Code Github-style Extension for Python Markdown

This extension adds Fenced Code Blocks to Python-Markdown.

    >>> import markdown
    >>> text = '''
    ... A paragraph before a fenced code block:
    ...
    ... ````
    ... Fenced code block
    ... ````
    ... '''
    >>> html = markdown.markdown(text, extensions=['fenced_code_gh'])
    >>> print html
    <p>A paragraph before a fenced code block:</p>
    <pre><code>Fenced code block
    </code></pre>

Works with safe_mode also (we check this because we are using the HtmlStash):

    >>> print markdown.markdown(text, extensions=['fenced_code_gh'], safe_mode='replace')
    <p>A paragraph before a fenced code block:</p>
    <pre><code>Fenced code block
    </code></pre>

Include tilde's in a code block and wrap with blank lines:

    >>> text = '''
    ... ````````
    ...
    ... ````
    ... ````````'''
    >>> print markdown.markdown(text, extensions=['fenced_code_gh'])
    <pre><code>
    ````
    </code></pre>

Language tags:

    >>> text = '''
    ... ````python
    ... # Some python code
    ... ````'''
    >>> print markdown.markdown(text, extensions=['fenced_code_gh'])
    <pre><code class="python"># Some python code
    </code></pre>

"""
import markdown
import re


RX_FENCED_BLOCK = re.compile(
    r'''(?P<fence>^`{3,})[ ]*(?P<lang>[^\n]+)?\n(?P<code>.*?)(?P=fence)[ ]*$''',
    re.MULTILINE|re.DOTALL
)
CODE_WRAP = '<pre><code%s>%s</code></pre>'
LANG_TAG = ' class="%s"'


class FencedCodeGhExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance.
        """
        md.registerExtension(self)

        md.preprocessors.add('fenced_code_block',
            FencedBlockPreprocessor(md),
            "_begin")


class FencedBlockPreprocessor(markdown.preprocessors.Preprocessor):

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash.
        """
        text = "\n".join(lines)
        while 1:
            m = RX_FENCED_BLOCK.search(text)
            if m:
                lang = ''
                if m.group('lang'):
                    lang = LANG_TAG % m.group('lang')

                code = ''.join([
                    '{% raw %}',
                    CODE_WRAP % (lang, self._escape(m.group('code'))),
                    '{% endraw %}'
                ])
                placeholder = self.markdown.htmlStash.store(code, safe=True)
                text = '%s\n%s\n%s'% (text[:m.start()], placeholder, text[m.end():])
            else:
                break
        return text.split("\n")

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def makeExtension(configs={}):
    return FencedCodeGhExtension(configs=configs)

