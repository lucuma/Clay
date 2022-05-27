import yaml

from clay.cli import cli


def set_config(dst, **config):
    (dst / "clay.yaml").write_text(yaml.safe_dump(config))


def test_exclude(dst):
    folder = dst / "nope" / "meh"
    folder.mkdir(parents=True, exist_ok=True)
    (dst / "nope" / "lorem.txt").touch()
    (dst / "nope" / "meh" / "ipsum.txt").touch()

    set_config(dst, exclude=["nope", "nope/*"])
    cli.build(source=dst)

    assert not (dst / "build" / "nope").exists()


def test_include(dst):
    folder = dst / "nope" / "meh"
    folder.mkdir(parents=True, exist_ok=True)
    (dst / "nope" / "lorem.txt").touch()
    (dst / "nope" / "a").touch()
    (dst / "nope" / "meh" / "b").touch()
    (dst / "nope" / "meh" / "ipsum.txt").touch()

    set_config(
        dst,
        exclude=["nope", "nope/*"],
        include=["nope/a", "nope/meh/b"]
    )
    cli.build(source=dst)

    assert (dst / "build" / "nope" / "a").exists()
    assert (dst / "build" / "nope" / "meh" / "b").exists()
    assert not (dst / "build" / "nope" / "lorem.txt").exists()
    assert not (dst / "build" / "nope" / "meh" / "ipsum.txt").exists()
