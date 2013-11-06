# -*- coding: utf-8 -*-
import os

import jinja2
import jinja2.ext

from .render import md_to_jinja


MARKDOWN_EXTENSION = '.md'


class MarkdownExtension(jinja2.ext.Extension):

    def preprocess(self, source, name, filename=None):
        if name is None or os.path.splitext(name)[1] != MARKDOWN_EXTENSION:
            return source
        return md_to_jinja(source)

    def _from_string(self, source, globals=None, template_class=None):
        env = self.environment
        globals = env.make_globals(globals)
        cls = template_class or env.template_class
        template_name = 'markdown_from_string.md'
        return cls.from_code(env, env.compile(source, template_name), globals, None)
