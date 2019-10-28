import os

import jinja2
from jinja2.sandbox import SandboxedEnvironment

from .jinja_includewith import IncludeWith


__all__ = ("ENVOPS_DEFAULT", "JinjaRender")

ENVOPS_DEFAULT = {
    "autoescape": False,
    "keep_trailing_newline": True,
    'extensions': ["jinja2.ext.with_", IncludeWith],
}


class JinjaRender(object):
    def __init__(self, src_path, data=None, envops=None):
        # Jinja <= 2.10 does not work with `pathlib.Path`s
        self.src_path = str(src_path)

        _envops = ENVOPS_DEFAULT.copy()
        _envops.update(envops or {})
        _envops.setdefault("loader", jinja2.FileSystemLoader(self.src_path))
        self.env = SandboxedEnvironment(**_envops)
        self.env.globals.update(**(data or {}))

    def __call__(self, fullpath, **data):
        relpath = str(fullpath).replace(self.src_path, "", 1).lstrip(os.path.sep)
        tmpl = self.env.get_template(relpath)
        return tmpl.render(**data)

    def string(self, string, **data):
        tmpl = self.env.from_string(string)
        return tmpl.render(**data)
