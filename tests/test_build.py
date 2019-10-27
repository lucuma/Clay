from datetime import datetime
import os

import clay


def test_render(dst):
    (dst / "test.txt").write_text("{{ now() }}")
    clay.cli.build(source=dst)

    expected = str(datetime.utcnow())[:-10]
    assert (dst / "build" / "test.txt").read_text().startswith(expected)


def test_custom_folder(dst):
    (dst / "test.txt").write_text("{{ now() }}")
    clay.cli.build(source=dst, folder="out")

    expected = str(datetime.utcnow())[:-10]
    assert (dst / "out" / "test.txt").read_text().startswith(expected)


def test_do_not_render_static(dst):
    text = "{{ now() }}"
    os.mkdir(dst / "static")
    (dst / "static" / "test.txt").write_text(text)
    clay.cli.build(source=dst)

    assert (dst / "build" / "static" / "test.txt").read_text() == text


def test_render_context(dst):
    (dst / "a.html").write_text("{{ request.path }}")
    (dst / "b.html").write_text("{{ request.path }}")
    clay.cli.build(source=dst)

    assert (dst / "build" / "a.html").read_text() == "a.html"
    assert (dst / "build" / "b.html").read_text() == "b.html"


def test_render_active(dst):
    os.mkdir(dst / "a")
    (dst / "a" / "index.html").write_text("{{ active('/') }}")
    (dst / "a" / "partial.html").write_text("{{ active('a', partial=true) }}")
    (dst / "a" / "no.html").write_text("{{ active('a') }}")
    (dst / "a" / "name.html").write_text("{{ active('name.html') }}")
    (dst / "a" / "exact.html").write_text("{{ active('a/exact.html') }}")
    (dst / "a" / "custom.html").write_text(
        "{{ active('a/custom.html', class_name='yeah') }}"
    )
    clay.cli.build(source=dst)

    # assert (dst / "build" / "a" / "index.html").read_text() == "active"
    assert (dst / "build" / "a" / "partial.html").read_text() == "active"
    assert (dst / "build" / "a" / "no.html").read_text() == ""
    assert (dst / "build" / "a" / "name.html").read_text() == ""
    assert (dst / "build" / "a" / "exact.html").read_text() == "active"
    assert (dst / "build" / "a" / "custom.html").read_text() == "yeah"
