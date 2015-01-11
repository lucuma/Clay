# -*- coding: utf-8 -*-
from datetime import datetime
from os.path import basename, join
import tempfile

from flask import (
    Flask, request, has_request_context, render_template, make_response
)
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from markupsafe import Markup
from moar import FileStorage, Thumbnailer

from .jinja_includewith import IncludeWith
from .markdown_ext import MarkdownExtension
from .tglobals import active, ToC


APP_NAME = 'clay'

TEMPLATE_GLOBALS = {
    'CLAY_URL': 'http://lucuma.github.com/Clay',
    'active': active,
    'now': datetime.utcnow(),
    'dir': dir,
    'enumerate': enumerate,
    'map': map,
    'zip': zip,
}


class WSGIApplication(Flask):

    def __init__(self, source_dir, build_dir, thumbs_url):
        super(WSGIApplication, self).__init__(
            APP_NAME, template_folder=source_dir, static_folder=None)
        self.jinja_loader = get_jinja_loader(source_dir)
        self.jinja_options = get_jinja_options()

        tempdir = tempfile.gettempdir()
        self.tempdir = tempdir
        storage = FileStorage(tempdir, base_url=thumbs_url)
        self.thumbnailer = Thumbnailer(source_dir, storage=storage)
        TEMPLATE_GLOBALS['thumbnail'] = self.thumbnailer

        toc = ToC(source_dir)

        def render_toc(*args, **kwargs):
            html = toc(*args, **kwargs)
            return Markup(html)

        TEMPLATE_GLOBALS['toc'] = render_toc

        self.build_dir = build_dir
        self.context_processor(lambda: TEMPLATE_GLOBALS)
        self.debug = True

    def get_test_client(self, host, port):
        self.testing = True
        self.config['SERVER_NAME'] = '%s:%s' % (host, port)
        return self.test_client()

    def render_template(self, path, context, host, port):
        if has_request_context():
            context.update(request.values.to_dict())
            return render_template(path, **context)

        self.thumbnailer.echo = not path.startswith('_index')
        self.thumbnailer.storage.base_url = '/'
        self.thumbnailer.storage.out_path = self.build_dir
        with self.test_request_context(
                '/' + path, method='GET',
                base_url='http://%s:%s' % (host, port)):
            return render_template(path, **context)

    def get_thumb_fullpath(self, thumbpath):
        return join(self.thumbnailer.storage.out_path, thumbpath)

    def response(self, content, status=200, mimetype='text/plain'):
        resp = make_response(content, status)
        resp.mimetype = mimetype
        return resp


def get_jinja_loader(source_dir):
    return ChoiceLoader([
        FileSystemLoader(source_dir),
        PackageLoader('clay', basename(source_dir)),
    ])


def get_jinja_options():
    return {
        'autoescape': True,
        'extensions': [MarkdownExtension, 'jinja2.ext.with_', IncludeWith],
    }
