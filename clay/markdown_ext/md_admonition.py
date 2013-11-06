# -*- coding: utf-8 -*-
"""
Admonition extension for Python-Markdown
=========================================

The syntax is as following:

    !!! [optional css classes]
        content here

A simple example:

    !!! note big
        This is the first line inside the box.

Outputs:

    <div class="admonition note big">
    <p>This is the first line inside the box.</p>
    </div>

"""
from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree

import re


CLASSNAME = 'admonition'
RX = re.compile(r'(?:^|\n)!!!\ ?([^\n]+)')


class AdmonitionProcessor(BlockProcessor):

    def test(self, parent, block):
        sibling = self.lastChild(parent)
        return RX.search(block) or \
            (block.startswith(' ' * self.tab_length) and sibling and \
                sibling.get('class', '').find(CLASSNAME) != -1)

    def run(self, parent, blocks):
        sibling = self.lastChild(parent)
        block = blocks.pop(0)
        m = RX.search(block)
        if m:
            block = block[m.end() + 1:]  # removes the first line
        block, theRest = self.detab(block)
        if m:
            klass = m.group(1)
            div = etree.SubElement(parent, 'div')
            div.set('class', '%s %s' % (CLASSNAME, klass))
        else:
            div = sibling
        self.parser.parseChunk(div, block)

        if theRest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, theRest)


class AdmonitionExtension(Extension):
    """ Admonition extension for Python-Markdown.
    """

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add(
            'admonition',
            AdmonitionProcessor(md.parser),
            '_begin'
        )
