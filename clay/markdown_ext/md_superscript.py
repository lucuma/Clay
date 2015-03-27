# coding=utf-8
"""
Superscipt extension for Markdown
==================================

Examples:

>>> import markdown
>>> md = markdown.Markdown(extensions=[SuperscriptExtension()])

>>> md.convert('lorem ipsum^1 sit.')
u'<p>lorem ipsum<sup>1</sup> sit.</p>'

>>> md.convert('6.02 x 10^23')
u'<p>6.02 x 10<sup>23</sup></p>'

>>> md.convert('10^(2x + 3).')
u'<p>10<sup>2x + 3</sup>.</p>'

"""
import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree, AtomicString


SUPER_RE = r'\^(?:([^\(\s]+)|\(([^\n\)]+)\))'


class SuperscriptPattern(Pattern):
    """ Return a superscript Element (`word^2^`). """
    def handleMatch(self, m):
        supr = m.group(2) or m.group(3)
        text = supr
        el = etree.Element("sup")
        el.text = AtomicString(text)
        return el


class SuperscriptExtension(markdown.Extension):
    """ Superscript Extension for Python-Markdown.
    """

    def extendMarkdown(self, md, md_globals):
        """ Replace superscript with SuperscriptPattern """
        md.inlinePatterns['superscript'] = SuperscriptPattern(SUPER_RE, md)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
