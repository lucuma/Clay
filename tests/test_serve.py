import os


def test_render(dst, server):
    (dst / "hello").write_text("{{ 'hello ' + 'world' }}")

    resp = server.get("/hello")
    assert resp.status == "200 OK"
    assert resp.text == "hello world"


def test_head(dst, server):
    (dst / "hello").write_text("{{ 'hello ' + 'world' }}")

    resp = server.head("/hello")
    assert resp.status == "200 OK"
    assert resp.text == ""


def test_not_found(dst, server):
    resp = server.get("/qwertyuio", expect_errors=True)

    assert resp.status == "404 Not Found"
    assert "not found" in resp.text


def test_filtered_not_found(dst, server):
    (dst / ".hello").write_text("world")
    os.mkdir(dst / ".foo")
    (dst / ".foo" / "bar").write_text("hello world")

    resp = server.get("/.hello", expect_errors=True)
    assert resp.status == "404 Not Found"
    assert "not found" in resp.text

    resp = server.get("/.foo/bar", expect_errors=True)
    assert resp.status == "404 Not Found"
    assert "not found" in resp.text


def test_custom_not_found(dst, server):
    (dst / "not-found.html").write_text("Custom not found")
    resp = server.get("/qwertyuio", expect_errors=True)

    assert resp.status == "404 Not Found"
    assert resp.text == "Custom not found"


def test_do_not_render_static(dst, server):
    text = "{{ now() }}"
    os.mkdir(dst / "static")
    (dst / "static" / "test.txt").write_text(text)

    resp = server.get("/static/test.txt")
    assert resp.text == text


def test_ajax(dst, server):
    (dst / "foobar").write_text("{{ 'ajax' if request.ajax else 'nope' }}")
    resp = server.get("/foobar", xhr=True)

    assert resp.text == "ajax"


def test_query(dst, server):
    (dst / "foobar").write_text(
        "{% for key, value in request.query.items() %}{{ key }}:{{ value }}/{% endfor %}")
    resp = server.get("/foobar?a=1&b=2&b=3", xhr=True)

    assert resp.text == "a:['1']/b:['2', '3']/"


def test_render_context(dst, server):
    (dst / "a.html").write_text("{{ request.path }}")
    (dst / "b.html").write_text("{{ request.path }}")

    assert server.get("/a.html").text == "a.html"
    assert server.get("/b.html").text == "b.html"


def test_render_active(dst, server):
    os.mkdir(dst / "a")
    (dst / "a" / "index.html").write_text("{{ active('/') }}")
    (dst / "a" / "partial.html").write_text("{{ active('a', partial=true) }}")
    (dst / "a" / "no.html").write_text("{{ active('a') }}")
    (dst / "a" / "name.html").write_text("{{ active('name.html') }}")
    (dst / "a" / "exact.html").write_text("{{ active('a/exact.html') }}")
    (dst / "a" / "custom.html").write_text(
        "{{ active('a/custom.html', class_name='yeah') }}"
    )

    # assert server.get("/a/index.html").text == "active"
    assert server.get("/a/partial.html").text == "active"
    assert server.get("/a/no.html").text == ""
    assert server.get("/a/name.html").text == ""
    assert server.get("/a/exact.html").text == "active"
    assert server.get("/a/custom.html").text == "yeah"


def test_old_thumbnailer(dst, server):
    (dst / "foobar").write_text("{{ thumbnail('image.png', [200, 100], foo='bar') }}")
    resp = server.get("/foobar", xhr=True)

    assert resp.text == "/image.png"


def test_folder_with_index_pattern(dst, server):
    (dst / "hello").mkdir()
    (dst / "hello" / "index.html").write_text("hello world")

    resp = server.get("/hello")
    assert resp.status == "200 OK"
    assert resp.text == "hello world"
