import filecmp
import os
import shutil
from pathlib import Path

from proper_cli import confirm, echo

from .active import make_active_helper
from .jinja_render import JinjaRender
from .request import Request
from .urls import make_absolute_urls_relative


__all__ = ("BlueprintRender", "printf")


def get_context(path=""):
    request = Request()
    request.path = str(path).replace("\\", "/").strip("/")
    active = make_active_helper(request)
    return {"request": request, "active": active}


class BlueprintRender:
    def __init__(
        self,
        src,
        dst,
        *,
        must_filter,
        is_binary,
        static_folder="static",
        force=False,
        globals_=None,
        filters_=None,
        **envops
    ):
        self.src = Path(src)
        self.dst = Path(dst)
        self.force = force
        self.must_filter = must_filter
        self.is_binary = is_binary
        self.static_folder = static_folder

        self.render = JinjaRender(src, globals_=globals_, filters_=filters_, **envops)

    def __call__(self, **data):
        src = str(self.src)
        for folder, _, files in os.walk(src):
            self.render_folder(Path(folder), files, **data)

    def render_folder(self, folder, files, **data):
        if self.must_filter(folder):
            return
        src = str(self.src)
        src_relfolder = str(folder).replace(src, "", 1).lstrip(os.path.sep)
        dst_relfolder = self.render.string(src_relfolder, **data)
        is_static = src_relfolder.startswith(self.static_folder)

        src_relfolder = Path(src_relfolder)
        dst_relfolder = Path(dst_relfolder)
        self._make_folder(dst_relfolder)

        for name in files:
            src_path = folder / name
            src_relpath = src_relfolder / name
            if self.must_filter(src_relpath):
                continue

            name = self.render.string(name, **data)
            dst_relpath = dst_relfolder / name

            if is_static or self.is_binary(src_relpath):
                self.copy_file(src_path, dst_relpath)
            else:
                self.render_file(src_relpath, dst_relpath, **data)

    def render_content(self, src_relpath, **data):
        if self.is_binary(src_relpath):
            return (self.src / src_relpath).read_bytes()
        return self.render(src_relpath, **data)

    def render_file(self, src_relpath, dst_relpath, **data):
        context = get_context(dst_relpath)
        context.update(data)
        content = self.render(src_relpath, **context)
        new_content = make_absolute_urls_relative(self.dst, dst_relpath, content)
        self.save_file(new_content, dst_relpath)

    def save_file(self, content, dst_relpath):
        dst_path = self.dst / dst_relpath
        if dst_path.exists():
            if self._contents_are_identical(content, dst_path):
                printf("identical", dst_relpath)
                return
            if not self._confirm_overwrite(dst_relpath):
                printf("skipped", dst_relpath, color="yellow")
                return
            printf("updated", dst_relpath, color="yellow")
        else:
            printf("created", dst_relpath, color="green")

        dst_path.write_text(content)

    def copy_file(self, src_path, dst_relpath):
        dst_path = self.dst / dst_relpath
        if dst_path.exists():
            if self._files_are_identical(src_path, dst_path):
                printf("identical", dst_relpath)
                return
            if not self._confirm_overwrite(dst_relpath):
                printf("skipped", dst_relpath, color="yellow")
                return
            printf("updated", dst_relpath, color="yellow")
        else:
            printf("created", dst_relpath, color="green")

        shutil.copy2(str(src_path), str(dst_path))

    # Private

    def _make_folder(self, rel_folder):
        path = self.dst / rel_folder
        if path.exists():
            return

        rel_folder = str(rel_folder).rstrip(".")
        display = f"{rel_folder}{os.path.sep}"
        path.mkdir(parents=False, exist_ok=False)
        if rel_folder:
            printf("created", display, color="green")

    def _files_are_identical(self, src_path, dst_path):
        return filecmp.cmp(str(src_path), str(dst_path), shallow=False)

    def _contents_are_identical(self, content, dst_path):
        return content == dst_path.read_text()

    def _confirm_overwrite(self, dst_relpath):
        printf("conflict", dst_relpath, color="red")
        if self.force:
            return True
        return confirm(" Overwrite?")


def printf(verb, msg="", color="cyan", indent=10):
    verb = str(verb).rjust(indent, " ")
    verb = f"<fg={color}>{verb}</>"
    echo(f"{verb}  {msg}".rstrip())
