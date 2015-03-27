# coding=utf-8
from __future__ import print_function

from os.path import dirname, join

from clay.tglobals import ToC


CLAY_SOURCE_PATH = join(dirname(__file__), u'..', u'clay')
FILTER = ('.*', '*.pyc', )


def test_toc_build():
    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)

    assert toc._leafs.items() == [
        (u'__init__.py', u'/__init__.py'),
        (u'helpers.py', u'/helpers.py'),
        (u'jinja_includewith.py', u'/jinja_includewith.py'),
        (u'main.py', u'/main.py'),
        (u'manage.py', u'/manage.py'),
        (u'server.py', u'/server.py'),
        (u'static.py', u'/static.py'),
        (u'tglobals.py', u'/tglobals.py'),
        (u'wsgiapp.py', u'/wsgiapp.py')
    ]
    assert toc._branches.keys() == [u'markdown_ext', u'source']


def test_toc_iter():
    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)

    assert list(toc) == [
        (u'__init__.py', u'/__init__.py'),
        (u'helpers.py', u'/helpers.py'),
        (u'jinja_includewith.py', u'/jinja_includewith.py'),
        (u'main.py', u'/main.py'),
        (u'manage.py', u'/manage.py'),
        (u'server.py', u'/server.py'),
        (u'static.py', u'/static.py'),
        (u'tglobals.py', u'/tglobals.py'),
        (u'wsgiapp.py', u'/wsgiapp.py')
    ]
    assert list(toc.source) == [
        (u'_index.html', u'/source/_index.html'),
        (u'_index.txt', u'/source/_index.txt'),
        (u'_notfound.html', u'/source/_notfound.html'),
    ]


def test_toc_render_maxdepth0():
    expected = """<ul class="toc">
    <li><a href="/__init__.py">__init__.py</a></li>
    <li><a href="/helpers.py">helpers.py</a></li>
    <li><a href="/jinja_includewith.py">jinja_includewith.py</a></li>
    <li><a href="/main.py">main.py</a></li>
    <li><a href="/manage.py">manage.py</a></li>
    <li><a href="/server.py">server.py</a></li>
    <li><a href="/static.py">static.py</a></li>
    <li><a href="/tglobals.py">tglobals.py</a></li>
    <li><a href="/wsgiapp.py">wsgiapp.py</a></li>
</ul>"""

    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)
    html = toc(maxdepth=0)
    assert expected == html


def test_toc_render_maxdepth1():
    expected = """<ul class="toc">
    <li><a href="/__init__.py">__init__.py</a></li>
    <li><a href="/helpers.py">helpers.py</a></li>
    <li><a href="/jinja_includewith.py">jinja_includewith.py</a></li>
    <li><a href="/main.py">main.py</a></li>
    <li><a href="/manage.py">manage.py</a></li>
    <li><a href="/server.py">server.py</a></li>
    <li><a href="/static.py">static.py</a></li>
    <li><a href="/tglobals.py">tglobals.py</a></li>
    <li><a href="/wsgiapp.py">wsgiapp.py</a></li>
    <li><span>markdown_ext</span>
        <ul class="toc">
            <li><a href="/markdown_ext/__init__.py">__init__.py</a></li>
            <li><a href="/markdown_ext/jinja.py">jinja.py</a></li>
            <li><a href="/markdown_ext/md_admonition.py">md_admonition.py</a></li>
            <li><a href="/markdown_ext/md_captions.py">md_captions.py</a></li>
            <li><a href="/markdown_ext/md_delinsmark.py">md_delinsmark.py</a></li>
            <li><a href="/markdown_ext/md_fencedcode.py">md_fencedcode.py</a></li>
            <li><a href="/markdown_ext/md_superscript.py">md_superscript.py</a></li>
            <li><a href="/markdown_ext/render.py">render.py</a></li>
        </ul>
    </li>
    <li><span>source</span>
        <ul class="toc">
            <li><a href="/source/_index.html">_index.html</a></li>
            <li><a href="/source/_index.txt">_index.txt</a></li>
            <li><a href="/source/_notfound.html">_notfound.html</a></li>
        </ul>
    </li>
</ul>"""

    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)
    html = toc(maxdepth=1)
    print(html)
    assert expected == html


def test_toc_render_maxdepthplus():
    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)
    assert toc(maxdepth=2) == toc(maxdepth=9999)


def test_toc_render_folders_first():
    expected = """<ul class="toc">
    <li><span>markdown_ext</span>
        <ul class="toc">
            <li><a href="/markdown_ext/__init__.py">__init__.py</a></li>
            <li><a href="/markdown_ext/jinja.py">jinja.py</a></li>
            <li><a href="/markdown_ext/md_admonition.py">md_admonition.py</a></li>
            <li><a href="/markdown_ext/md_captions.py">md_captions.py</a></li>
            <li><a href="/markdown_ext/md_delinsmark.py">md_delinsmark.py</a></li>
            <li><a href="/markdown_ext/md_fencedcode.py">md_fencedcode.py</a></li>
            <li><a href="/markdown_ext/md_superscript.py">md_superscript.py</a></li>
            <li><a href="/markdown_ext/render.py">render.py</a></li>
        </ul>
    </li>
    <li><span>source</span>
        <ul class="toc">
            <li><a href="/source/_index.html">_index.html</a></li>
            <li><a href="/source/_index.txt">_index.txt</a></li>
            <li><a href="/source/_notfound.html">_notfound.html</a></li>
        </ul>
    </li>
    <li><a href="/__init__.py">__init__.py</a></li>
    <li><a href="/helpers.py">helpers.py</a></li>
    <li><a href="/jinja_includewith.py">jinja_includewith.py</a></li>
    <li><a href="/main.py">main.py</a></li>
    <li><a href="/manage.py">manage.py</a></li>
    <li><a href="/server.py">server.py</a></li>
    <li><a href="/static.py">static.py</a></li>
    <li><a href="/tglobals.py">tglobals.py</a></li>
    <li><a href="/wsgiapp.py">wsgiapp.py</a></li>
</ul>"""

    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)
    html = toc(maxdepth=1, folders_first=True)
    print(html)
    assert expected == html
