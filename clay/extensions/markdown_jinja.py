# -*- coding: utf-8 -*-
"""
# Clay.extensions.markdown_jinja

A markdown pre-compiler for jinja templates.

"""
import re
import os.path

from jinja2 import Environment, TemplateSyntaxError
from jinja2.ext import Extension


class HamlishExtension(Extension):

    def __init__(self, environment):
        super(HamlishExtension, self).__init__(environment)

        environment.extend(
            hamlish_mode='compact',
            hamlish_file_extensions=('.haml',),
            hamlish_indent_string='    ',
            hamlish_newline_string='\n',
            hamlish_debug=False,
            hamlish_enable_div_shortcut=False,
        )


    def preprocess(self, source, name, filename=None):
        if not os.path.splitext(name)[1] in \
            self.environment.hamlish_file_extensions:
            return source

        h = self.get_preprocessor(self.environment.hamlish_mode)
        try:
            return h.convert_source(source)
        except TemplateIndentationError, e:
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)
        except TemplateSyntaxError, e:
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)


    def get_preprocessor(self, mode):

        if mode == 'compact':
            output = Output(indent_string='', newline_string='')
        elif mode == 'debug':
            output = Output(indent_string='   ', newline_string='\n', debug=True)
        else:
            output = Output(indent_string=self.environment.hamlish_indent_string,
                        newline_string=self.environment.hamlish_newline_string,
                        debug=self.environment.hamlish_debug)

        return Hamlish(output, self.environment.hamlish_enable_div_shortcut)

