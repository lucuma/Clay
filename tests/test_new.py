import clay


def test_new_cwd(dst):
    dest = dst / "demo"
    clay.cli.new(dest)
    assert (dest / "static").is_dir()
    assert (dest / "clay.yaml").is_file()
