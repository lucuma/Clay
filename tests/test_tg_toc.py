from os.path import dirname, join
import shutil

from clay.tglobals import ToC


CLAY_SOURCE_PATH = join(dirname(__file__), '..', 'clay')
FILTER = ('.*', '*.pyc', '__pycache__' )


def setup_function(function):
    try:
        shutil.rmtree(join(CLAY_SOURCE_PATH, '__pycache__'))
    except OSError:
        pass


def test_toc_build():
    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)

    assert list(toc._leafs.items()) == [
        ('__init__.py', '/__init__.py'),
        ('helpers.py', '/helpers.py'),
        ('jinja_includewith.py', '/jinja_includewith.py'),
        ('main.py', '/main.py'),
        ('manage.py', '/manage.py'),
        ('server.py', '/server.py'),
        ('static.py', '/static.py'),
        ('tglobals.py', '/tglobals.py'),
        ('wsgiapp.py', '/wsgiapp.py')
    ]
    assert list(toc._branches.keys()) == ['markdown_ext', 'source']


def test_toc_iter():
    toc = ToC(CLAY_SOURCE_PATH, filter=FILTER)

    assert list(toc) == [
        ('__init__.py', '/__init__.py'),
        ('helpers.py', '/helpers.py'),
        ('jinja_includewith.py', '/jinja_includewith.py'),
        ('main.py', '/main.py'),
        ('manage.py', '/manage.py'),
        ('server.py', '/server.py'),
        ('static.py', '/static.py'),
        ('tglobals.py', '/tglobals.py'),
        ('wsgiapp.py', '/wsgiapp.py')
    ]
    assert list(toc.source) == [
        ('_index.html', '/source/_index.html'),
        ('_index.txt', '/source/_index.txt'),
        ('_notfound.html', '/source/_notfound.html'),
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
