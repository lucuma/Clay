import os

import jinja2
from jinja2.sandbox import SandboxedEnvironment


__all__ = ("ENVOPS_DEFAULT", "JinjaRender")

ENVOPS_DEFAULT = {
    "autoescape": False,
    "keep_trailing_newline": True,
}


class JinjaRender:
    def __init__(self, src_path, data=None, filters_=None, **envops):
        self.src_path = str(src_path)
        _envops = ENVOPS_DEFAULT.copy()
        _envops.update(envops or {})
        _envops.setdefault("loader", jinja2.FileSystemLoader(self.src_path))
        self.env = SandboxedEnvironment(**_envops)
        self.env.filters.update(filters_ or {})
        self.env.globals.update(**(data or {}))

    def __call__(self, fullpath, **data):
        relpath = str(fullpath).replace(self.src_path, "", 1).lstrip(os.path.sep)
        tmpl = self.env.get_template(relpath)
        return tmpl.render(**data)

    def string(self, string, **data):
        tmpl = self.env.from_string(string)
        return tmpl.render(**data)
