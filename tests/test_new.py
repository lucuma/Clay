from clay.cli import cli


def test_new_cwd(dst):
    dest = dst / "demo"
    cli.new(dest)
    assert (dest / "static").is_dir()
    assert (dest / "clay.yaml").is_file()
