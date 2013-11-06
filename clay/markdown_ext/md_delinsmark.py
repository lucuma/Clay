# -*- coding: utf-8 -*-
"""
Del/Ins/Mark Extension for Markdown
====================================

Wraps the inline content with ins/del tags.

Example:

>>> import markdown
>>> md = markdown.Markdown(extensions=[DelInsMarkExtension()])

>>> md.convert('This is ++added content++, this is ~~deleted content~~ and this is ==marked==.')
u'<p>This is <ins>added content</ins>, this is <del>deleted content</del> and this is <mark>marked</mark>.</p>'

"""
import markdown
from markdown.inlinepatterns import SimpleTagPattern


DEL_RE = r"(\~\~)(.+?)(\~\~)"
INS_RE = r"(\+\+)(.+?)(\+\+)"
MARK_RE = r"(\=\=)(.+?)(\=\=)"


class DelInsMarkExtension(markdown.extensions.Extension):
    """Adds del_ins extension to Markdown class.
    """

    def extendMarkdown(self, md, md_globals):
        """Modifies inline patterns."""
        md.inlinePatterns.add('del', SimpleTagPattern(DEL_RE, 'del'), '<not_strong')
        md.inlinePatterns.add('ins', SimpleTagPattern(INS_RE, 'ins'), '<not_strong')
        md.inlinePatterns.add('mark', SimpleTagPattern(MARK_RE, 'mark'), '<not_strong')


if __name__ == "__main__":
    import doctest
    doctest.testmod()
