# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime
import mimetypes
import os
from os.path import (isfile, isdir, dirname, join, splitext, split, exists,
    relpath, sep)
import re

from flask import (Flask, request, has_request_context, render_template,
    send_file, make_response)
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
import yaml

from .helpers import (read_content, make_dirs, create_file,
    copy_if_updated, get_updated_datetime)
from .tglobals import link_to


SOURCE_DIRNAME = 'source'
BUILD_DIRNAME = 'build'
TMPL_EXTS = ('.html', '.tmpl')
RX_TMPL = re.compile(r'\.tmpl$')

HTTP_NOT_FOUND = 404

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080

SOURCE_NOT_FOUND_HELP = """We couldn't found a "%s" dir.
Are you sure you're in the correct folder? """ % SOURCE_DIRNAME

rx_abs_url = re.compile(r'\s(?P<attr>src|href)=[\'"]\/(?P<url>([a-z0-9][^\'"]*)?)[\'"]',
    re.UNICODE | re.IGNORECASE)


class Clay(object):

    def __init__(self, root, settings=None):
        if isfile(root):
            root = dirname(root)
        settings = settings or {}
        self.settings = settings
        self.settings_path = join(root, 'settings.yml')
        self.load_settings_from_file()
        self.source_dir = join(root, SOURCE_DIRNAME)
        self.build_dir = join(root, BUILD_DIRNAME)
        self.app = self.make_app()

    def make_app(self):
        app = Flask('clay', static_folder=None, template_folder=self.source_dir)
        app.jinja_loader = self.get_jinja_loader()
        app.jinja_options = self.get_jinja_options()
        app.debug = True
        self.set_template_context_processors(app)
        self.set_urls(app)
        return app

    def get_jinja_loader(self):
        return ChoiceLoader([
            FileSystemLoader(self.source_dir),
            PackageLoader('clay', SOURCE_DIRNAME),
        ])

    def get_jinja_options(self):
        e = ['jinja2.ext.autoescape', 'jinja2.ext.with_']
        return {'extensions': e}

    def set_template_context_processors(self, app):
        @app.context_processor
        def inject_globals():
            return {
                'CLAY_URL': 'http://lucuma.github.com/Clay',

                'now': datetime.utcnow(),
                'enumerate': enumerate,
                'link_to': link_to,
            }

    def set_urls(self, app):
        app.add_url_rule('/', 'page', self.render_page)
        app.add_url_rule('/<path:path>', 'page', self.render_page)
        app.add_url_rule('/_index.html', 'index', self.show__index)

    def load_settings_from_file(self):
        if isfile(self.settings_path):
            source = read_content(self.settings_path)
            st = yaml.load(source)
            self.settings.update(st)

    def render(self, path, context):
        if has_request_context():
            return render_template(path, **context)
        with self.app.test_request_context('/' + path, method='GET'):
            return render_template(path, **context)

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

    def get_relpath(self, folder):
        rel = relpath(folder, self.source_dir)
        return rel.lstrip('.').lstrip(sep)

    def get_run_config(self, host, port):
        port = port or self.settings.get('port', DEFAULT_PORT)
        return {
            'host': host or self.settings.get('host', DEFAULT_HOST),
            'port': int(port),
            'use_debugger': True,
            'use_reloader': False,
        }

    def remove_template_ext(self, path):
        return RX_TMPL.sub('', path)

    def get_relative_url(self, relpath, currurl):
        depth = relpath.count('/')
        url = (ur'../' * depth) + currurl
        if not url:
            return 'index.html'
        path = self.get_full_source_path(url)
        if isdir(path) or url.endswith('/'):
            return url.rstrip('/') + '/index.html'
        return url

    def make_absolute_urls_relative(self, content, relpath):
        match = rx_abs_url.search(content)
        if not match:
            return content

        url = self.get_relative_url(relpath, match.group('url'))
        repl = ur' %s="%s"' % (match.group('attr'), url)
        return re.sub(rx_abs_url, repl, content)

    def is_html_fragment(self, content):
        head = content[:500].strip().lower()
        return not (head.startswith('<!doctype ') or head.startswith('<html'))

    def must_be_filtered(self, path, content):
        if path in self.settings.get('INCLUDE', []):
            return False

        r1 = self.settings.get('FILTER_PARTIALS') and self.is_html_fragment(content)
        r2 = path in self.settings.get('FILTER', [])
        return r1 or r2

    def get_pages_list(self):
        pages = []
        for folder, subs, files in os.walk(self.source_dir):
            rel = self.get_relpath(folder)
            for filename in files:
                pages.append(join(rel, filename))
        return pages

    def get_pages_index(self):
        index = []
        pages = self.get_pages_list()
        for path in pages:
            fullpath = self.get_full_source_path(path)
            updated_at = get_updated_datetime(fullpath)

            if not path.endswith(TMPL_EXTS):
                index.append((path, updated_at))
                continue

            content = self.render(path, self.settings)
            if self.must_be_filtered(path, content):
                continue
            index.append((path, updated_at))
        return index

    def send_file(self, path):
        fp = self.get_full_source_path(path)
        return send_file(fp)

    def render_page(self, path=None):
        path = self.normalize_path(path)

        if not path.endswith(TMPL_EXTS):
            return self.send_file(path)

        res = self.render(path, self.settings)
        response = make_response(res)
        response.mimetype = self.guess_mimetype(self.get_real_fn(path))
        return response

    def show__index(self):
        index = self.get_pages_index()
        context = self.settings.copy()
        context['index'] = index
        res = self.render('_index.html', context)
        return make_response(res)

    def build__index(self):
        path = '_index.html'
        bp = self.get_full_build_path(path)
        index = self.get_pages_index()
        context = self.settings.copy()
        context['index'] = index
        content = self.render(path, context)
        create_file(bp, content)

    def build_page(self, path):
        sp = self.get_full_source_path(path)
        bp = self.get_full_build_path(path)
        make_dirs(dirname(bp))

        if not path.endswith(TMPL_EXTS):
            return copy_if_updated(sp, bp)

        content = self.render(path, self.settings)

        if self.must_be_filtered(path, content):
            return

        bp = self.remove_template_ext(bp)
        if bp.endswith('.html'):
            content = self.make_absolute_urls_relative(content, path)
        create_file(bp, content)

    def run(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        if not exists(self.source_dir):
            print SOURCE_NOT_FOUND_HELP
            return
        config = self.get_run_config(host, port)
        return self.app.run(**config)

    def build(self):
        pages = self.get_pages_list()
        for path in pages:
            self.build_page(path)
        self.build__index()

    def get_test_client(self):
        self.app.testing = True
        return self.app.test_client()

