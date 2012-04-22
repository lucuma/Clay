"""
Table of Contents Extension for Python-Markdown
* * *

(c) 2008 [Jack Miller](http://codezen.org)

Dependencies:
* [Markdown 2.1+](http://www.freewisdom.org/projects/python-markdown/)

"""
import markdown
from markdown.util import etree
from markdown.extensions.headerid import slugify, unique, itertext

import re


class TocTreeprocessor(markdown.treeprocessors.Treeprocessor):
    # Iterator wrapper to get parent and child all at once
    def iterparent(self, root):
        for parent in root.getiterator():
            for child in parent:
                yield parent, child

    def run(self, doc):
        div = etree.Element("div")
        last_li = None

        level = 0
        list_stack=[div]
        header_rgx = re.compile("[Hh][123456]")

        # Get a list of id attributes
        used_ids = []
        for c in doc.getiterator():
            if "id" in c.attrib:
                used_ids.append(c.attrib["id"])

        for (p, c) in self.iterparent(doc):
            text = ''.join(itertext(c)).strip()
            if not text:
                continue
                    
            if header_rgx.match(c.tag):
                try:
                    tag_level = int(c.tag[-1])
                    
                    while tag_level < level:
                        list_stack.pop()
                        level -= 1

                    if tag_level > level:
                        newlist = etree.Element("ul")
                        if last_li:
                            last_li.append(newlist)
                        else:
                            list_stack[-1].append(newlist)
                        list_stack.append(newlist)

                        if level == 0:
                            level = tag_level
                        else:
                            level += 1

                    # Do not override pre-existing ids 
                    if not "id" in c.attrib:
                        id = unique(self.config["slugify"](text, '-'), used_ids)
                        c.attrib["id"] = id
                    else:
                        id = c.attrib["id"]

                    # List item link, to be inserted into the toc
                    last_li = etree.Element("li")
                    link = etree.SubElement(last_li, "a")
                    link.text = text
                    link.attrib["href"] = '#' + id

                    if self.config["anchorlink"]:
                        anchor = etree.Element("a")
                        anchor.text = c.text
                        anchor.attrib["href"] = "#" + id
                        anchor.attrib["class"] = "toclink"
                        c.text = ""
                        for elem in c.getchildren():
                            anchor.append(elem)
                            c.remove(elem)
                        c.append(anchor)

                    list_stack[-1].append(last_li)
                except IndexError:
                    # We have bad ordering of headers. Just move on.
                    pass
        
        # searialize and attach to markdown instance.
        ul = div.find('ul')
        if not ul:
            self.markdown.toc = ''
            return
        
        ul.attrib["class"] = "toc"
        toc = self.markdown.serializer(ul)
        for pp in self.markdown.postprocessors.values():
            toc = pp.run(toc)
        self.markdown.toc = toc


class TocExtension(markdown.Extension):

    def __init__(self, **configs):
        self.config = {
            "slugify" : [slugify,
                "Function to generate anchors based on header text-"
                "Defaults to the headerid ext's slugify function."
            ],
            "anchorlink" : [True,
                "True if header should be a self link"
                "Defaults to 0"
            ],
        }
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        tocext = TocTreeprocessor(md)
        tocext.config = self.getConfigs()
        # Headerid ext is set to '>inline'. With this set to '<prettify',
        # it should always come after headerid ext (and honor ids assinged 
        # by the header id extension) if both are used. Same goes for 
        # attr_list extension. This must come last because we don't want
        # to redefine ids after toc is created. But we do want toc prettified.
        md.treeprocessors.add("toc", tocext, "<prettify")

	
def makeExtension(configs={}):
    return TocExtension(configs=configs)

