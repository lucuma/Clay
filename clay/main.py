# -*- coding: utf-8 -*-
import mimetypes
from os.path import isfile, isdir, dirname, join, splitext, split

from flask import Flask, send_file, make_response
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader, TemplateNotFound

from helpers import Render, make_dirs, create_file, copy_if_updated


SOURCE_DIRNAME = 'source'
BUILD_DIRNAME = 'build'
TMPL_EXTS = ('.html', '.tmpl')
HTTP_NOT_FOUND = 404

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5000


class Clay(object):

    def __init__(self, root, settings=None):
        settings = settings or {}
        self.settings = settings

        if isfile(root):
            root = dirname(root)
        self.source_dir = join(root, SOURCE_DIRNAME)
        self.build_dir = join(root, BUILD_DIRNAME)
        self.app = self.make_app()
        self.render = self.make_renderer()

    def get_full_source_path(self, path):
        return join(self.source_dir, path)

    def get_full_build_path(self, path):
        return join(self.build_dir, path)

    def get_real_fn(self, path):
        head, tail = split(path)
        if tail.endswith('.html'):
            return tail
        fn, ext = splitext(tail)
        return fn

    def guess_mimetype(self, fn):
        return mimetypes.guess_type(fn)[0] or 'text/plain'

    def normalize_path(self, path):
        path = path or 'index.html'
        if isdir(self.get_full_source_path(path)):
            path = '/'.join([path, 'index.html'])
        return path

    def make_build_dir(self):
        if not isdir(self.build_dir):
            make_dirs(self.build_dir)


    def make_app(self):
        app = Flask('clay')
        app.debug = True
        self.add_default_urls(app)
        self.set_not_found_handler(app)
        return app

    def make_renderer(self):
        loader = self.make_jinja_loader()
        render = Render(loader)
        return render

    def make_jinja_loader(self):
        return ChoiceLoader([
            FileSystemLoader(self.source_dir),
            PackageLoader('clay', SOURCE_DIRNAME),
        ])

    def add_default_urls(self, app):
        app.add_url_rule('/', 'page', self.render_page)
        app.add_url_rule('/<path:path>', 'page', self.render_page)

    def set_not_found_handler(self, app):
        @app.errorhandler(HTTP_NOT_FOUND)
        @app.errorhandler(TemplateNotFound)
        def page_not_found(error):
            res = self.render('notfound.html', self.settings)
            return make_response(res, HTTP_NOT_FOUND)


    def render_page(self, path=None):
        path = self.normalize_path(path)

        if not path.endswith(TMPL_EXTS):
            return self.send_file(path)

        res = self.render(path, self.settings)
        response = make_response(res)
        response.mimetype = self.guess_mimetype(self.get_real_fn(path))
        return response

    def send_file(self, path):
        fp = self.get_full_source_path(path)
        return send_file(fp)

    def get_test_client(self):
        self.app.testing = True
        return self.app.test_client()

    def build_page(self, path):
        self.make_build_dir()
        spath = self.get_full_source_path(path)
        bpath = self.get_full_build_path(path)
        
        if not path.endswith(TMPL_EXTS):
            return copy_if_updated(spath, bpath)

        content = self.render(path)
        create_file(bpath, content)

    def run(self, host=DEFAULT_HOST, port=DEFAULT_PORT, _test=False):
        config = {
            'host': host or self.settings.get('host', DEFAULT_HOST),
            'port': port or self.settings.get('port', DEFAULT_PORT),
            'use_debugger': True,
            'use_reloader': False,
        }
        if _test:
            return config
        self.app.run(**config)

