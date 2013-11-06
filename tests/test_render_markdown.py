# -*- coding: utf-8 -*-
from __future__ import print_function

from .helpers import *


def test_basic_md(t):
    content = '''
Roses are red;
Violets are blue.

Hello world!
'''
    expected = '''
<p>Roses are red;<br>
Violets are blue.</p>
<p>Hello world!</p>
'''
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()


def test_layout(t):
    base = '''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{% block title %}{% endblock %}</title>
</head>
<body>{% block content %}{% endblock %}</body>
</html>
'''

    content = '''layout: base.html
title: Hello world

# Hi
'''

    expected = '''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Hello world</title>
</head>
<body><h1 id="hi">Hi</h1></body>
</html>
'''

    create_file(get_source_path('base.html'), base)
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()


def test_fenced_code(t):
    content = '''
Plain:

```
pip install clay
```

Highlighted:

```python
print('hi')
```
'''
    expected = '''
<p>Plain:</p>
<pre><code>pip install clay
</code></pre>


<p>Highlighted:</p>
<pre><code class="language-python"><span class="k">print</span><span class="p">(</span><span class="s">&#39;hi&#39;</span><span class="p">)</span>
</code></pre>
'''
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()


def test_protect_jinja_code(t):
    content = '''
```jinja
{{ protect_me }}
```
'''
    expected = '''
<pre><code class="language-jinja"><span class="cp">{{</span> <span class="nv">protect_me</span> <span class="cp">}}</span><span class="x"></span>
</code></pre>
'''
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()


def test_admonition(t):
    content = '''
!!! note clear
    This is the first line inside the box.
    This is [an example](http://example.com/) inline link.

    Another paragraph
'''
    expected = '''
<div class="admonition note clear">
<p>This is the first line inside the box.<br>
This is <a href="http://example.com/">an example</a> inline link.</p>
<p>Another paragraph</p>
</div>
'''
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()


def test_superscript(t):
    content = '''
lorem ipsum^1 sit.

6.02 x 10^23

10^(2x + 3).
'''
    expected = '''
<p>lorem ipsum<sup>1</sup> sit.</p>
<p>6.02 x 10<sup>23</sup></p>
<p>10<sup>2x + 3</sup>.</p>
'''
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()


def test_delinsmark(t):
    content = '''
This is ++added content++, this is ~~deleted content~~ and this is ==marked==.
'''
    expected = '''
<p>This is <ins>added content</ins>, this is <del>deleted content</del> and this is <mark>marked</mark>.</p>
'''
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()


def test_autolink(t):
    content = '''
http://example.com/

go to http://example.com. Now!

ftp://example.com

www.example.com

WWW.EXAMPLE.COM

www.example.pe

(www.example.us/path/?name=val)

----------

like something.com or whatever

punto.pe

<a href="http://example.com/">http://example.com/</a>

<a href="www.example.org/" title="www.example.net" class="blue">http://example.org/</a>

info@example.com

<a href="mailto:info@example.com">write us</a>
'''
    expected = '''
<p><a href="http://example.com/">http://example.com/</a></p>
<p>go to <a href="http://example.com">http://example.com</a>. Now!</p>
<p><a href="ftp://example.com">ftp://example.com</a></p>
<p><a href="http://www.example.com">www.example.com</a></p>
<p><a href="http://WWW.EXAMPLE.COM">WWW.EXAMPLE.COM</a></p>
<p><a href="http://www.example.pe">www.example.pe</a></p>
<p>(<a href="http://www.example.us/path/?name=val">www.example.us/path/?name=val</a>)</p>
<hr>
<p>like something.com or whatever</p>
<p>punto.pe</p>
<p><a href="http://example.com/">http://example.com/</a></p>
<p><a href="www.example.org/" title="www.example.net" class="blue">http://example.org/</a></p>
<p>info@example.com</p>
<p><a href="mailto:info@example.com">write us</a></p>
'''
    path = get_source_path('test.md')
    create_file(path, content)
    resp = t.get('/test.md')
    assert resp.status_code == HTTP_OK
    assert resp.mimetype == 'text/html'
    print(resp.data)
    assert resp.data.strip() == expected.strip()
