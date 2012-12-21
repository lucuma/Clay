# -*- coding: utf-8 -*-
from datetime import datetime
import errno
import io
import os
import re
import shutil

from flask import request
import jinja2
from werkzeug.local import LocalProxy


class Render(object):
    """A thin wrapper arround Jinja2.
    """

    default_globals = {
        'now': LocalProxy(datetime.utcnow),
        'enumerate': enumerate,
        'request': request,
    }

    def __init__(self, loader, **kwargs):
        kwargs.setdefault('autoescape', True)
        env = jinja2.Environment(loader=loader, **kwargs)
        env.globals.update(self.default_globals)
        self.env = env

    def render(self, tmpl, context=None):
        context = context or {}
        return tmpl.render(context)

    def __call__(self, filename, context=None):
        tmpl = self.env.get_template(filename)
        return self.render(tmpl, context)
    
    # def from_string(self, source, context=None):
    #     tmpl = self.env.from_string(source)
    #     return self.render(tmpl, context)


def read_content(path, **kwargs):
    kwargs.setdefault('mode', 'rt')
    with io.open(path, **kwargs) as f:
        return f.read()


def make_dirs(*lpath):
    path = os.path.join(*lpath)
    try:
        os.makedirs(path)
    except (OSError), e:
        if e.errno != errno.EEXIST:
            raise
    return path


def create_file(path, content, encoding='utf8'):
    if not isinstance(content, unicode):
        content = unicode(content, encoding)
    with io.open(path, 'w+t', encoding=encoding) as f:
        f.write(content)


def copy_if_updated(path_in, path_out):
    if os.path.exists(path_out):
        newt = os.path.getmtime(path_in)
        currt = os.path.getmtime(path_out)
        if currt >= newt:
            return
    shutil.copy2(path_in, path_out)


