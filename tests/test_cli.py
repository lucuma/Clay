import os
from datetime import datetime

from clay.cli import cli


def test_new_cwd(dst):
    dest = dst / "demo"
    cli.new(dest)
    assert (dest / "static").is_dir()
    assert (dest / "clay.yaml").is_file()


def test_render(dst):
    (dst / "test.txt").write_text("{{ now() }}")
    cli.build(source=dst)

    expected = str(datetime.utcnow())[:-10]
    assert (dst / "build" / "test.txt").read_text().startswith(expected)


def test_do_not_render_static(dst):
    text = "{{ now() }}"
    os.mkdir(dst / "static")
    (dst / "static" / "test.txt").write_text(text)
    (dst / "static" / "test.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    cli.build(source=dst)

    assert (dst / "build" / "static" / "test.txt").read_text() == text
    assert (dst / "build" / "static" / "test.png").is_file()


def test_do_not_render_static_subfolders(dst):
    text = "{{ now() }}"
    folder = dst / "static" / "meh"
    folder.mkdir(parents=True, exist_ok=True)
    (dst / "static" / "meh" / "test.txt").write_text(text)
    (dst / "static" / "meh" / "test.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    cli.build(source=dst)
    assert (dst / "build" / "static" / "meh" / "test.txt").read_text() == text
    assert (dst / "build" / "static" / "meh" / "test.png").is_file()


def test_do_not_render_binary_with_known_extendions(dst):
    (dst / "test.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    cli.build(source=dst)

    assert (dst / "build" / "test.png").is_file()


def test_render_context(dst):
    (dst / "a.html").write_text("{{ request.path }}")
    (dst / "b.html").write_text("{{ request.path }}")
    cli.build(source=dst)

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
    cli.build(source=dst)

    # assert (dst / "build" / "a" / "index.html").read_text() == "active"
    assert (dst / "build" / "a" / "partial.html").read_text() == "active"
    assert (dst / "build" / "a" / "no.html").read_text() == ""
    assert (dst / "build" / "a" / "name.html").read_text() == ""
    assert (dst / "build" / "a" / "exact.html").read_text() == "active"
    assert (dst / "build" / "a" / "custom.html").read_text() == "yeah"
