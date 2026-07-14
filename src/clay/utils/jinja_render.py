import jinja2
from jinja2.sandbox import SandboxedEnvironment


class JinjaRender:
    @property
    def globals(self):
        return self.env.globals

    @property
    def filters(self):
        return self.env.filters

    @property
    def tests(self):
        return self.env.tests

    def __init__(self, src_path, globals_=None, filters_=None, **envops):
        envops["loader"] = jinja2.FileSystemLoader(str(src_path))
        envops.setdefault("autoescape", False)
        envops.setdefault("keep_trailing_newline", True)
        self.env = SandboxedEnvironment(**envops)
        self.env.filters.update(filters_ or {})
        self.env.globals.update(**(globals_ or {}))

    def __call__(self, relpath, **data):
        relpath = str(relpath)
        return self.render(relpath, **data)

    def render(self, relpath, **data):
        relpath = str(relpath)
        tmpl = self.env.get_template(relpath)
        return tmpl.render(**data)

    def string(self, string, **data):
        tmpl = self.env.from_string(string)
        return tmpl.render(**data)
