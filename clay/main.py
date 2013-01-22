# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime
import mimetypes
import os
from os.path import (isfile, isdir, dirname, join, splitext, basename, exists,
    relpath, sep)
import re

from flask import (Flask, request, has_request_context, render_template,
    make_response, abort, send_file)
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from jinja2.exceptions import TemplateNotFound
import yaml

from .helpers import (read_content, make_dirs, create_file,
    copy_if_updated, get_updated_datetime)
from .jinja_includewith import IncludeWith
from .server import Server, DEFAULT_HOST, DEFAULT_PORT
from .tglobals import active, to_unicode


SOURCE_DIRNAME = 'source'
BUILD_DIRNAME = 'build'
TMPL_EXTS = ('.html', '.tmpl')
RX_TMPL = re.compile(r'\.tmpl$')

HTTP_NOT_FOUND = 404

SOURCE_NOT_FOUND = u"""We couldn't found a "%s" dir.
Are you sure you're in the correct folder? """ % SOURCE_DIRNAME

rx_abs_url = re.compile(r'\s(src|href|data-[a-z0-9_-]+)\s*=\s*[\'"](\/(?:[a-z0-9_-][^\'"]*)?)[\'"]',
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
        self.server = Server(self)

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
        return {
            'autoescape': True,
            'extensions': ['jinja2.ext.with_', IncludeWith]
            }

    def set_template_context_processors(self, app):
        @app.context_processor
        def inject_globals():
            return {
                'CLAY_URL': 'http://lucuma.github.com/Clay',
                'active': active,
                'now': datetime.utcnow(),
                'dir': dir,
                'enumerate': enumerate,
                'map': map,
                'zip': zip,
            }

    def set_urls(self, app):
        app.add_url_rule('/', 'page', self.render_page)
        app.add_url_rule('/<path:path>', 'page', self.render_page)
        app.add_url_rule('/_index.html', 'index', self.show__index)
        app.add_url_rule('/_index.txt', 'index_txt', self.show__index_txt)

    def load_settings_from_file(self):
        if isfile(self.settings_path):
            source = read_content(self.settings_path)
            st = yaml.load(source)
            self.settings.update(st)

    def _get_base_url(self):
        host = self.settings.get('host', DEFAULT_HOST)
        port = self.settings.get('port', DEFAULT_PORT)
        return 'http://%s:%s' % (host, port)

    def render(self, path, context):
        if has_request_context():
            return render_template(path, **context)

        base_url = self._get_base_url()
        with self.app.test_request_context('/' + path, base_url=base_url, method='GET'):
            return render_template(path, **context)

    def get_full_source_path(self, path):
        return join(self.source_dir, path)

    def get_full_build_path(self, path):
        return join(self.build_dir, path)

    def get_real_fn(self, path):
        filename = basename(path)
        fn, ext = splitext(filename)
        fn2, ext2 = splitext(fn)
        if ext2:
            return fn
        return filename

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

    def remove_template_ext(self, path):
        return RX_TMPL.sub('', path)

    def get_relative_url(self, relpath, currurl):
        depth = relpath.count('/')
        url = (ur'../' * depth) + currurl.lstrip('/')
        if not url:
            return 'index.html'
        path = self.get_full_source_path(url)
        if isdir(path) or url.endswith('/'):
            return url.rstrip('/') + '/index.html'
        return url

    def make_absolute_urls_relative(self, content, relpath):
        for attr, url in rx_abs_url.findall(content):
            newurl = self.get_relative_url(relpath, url)
            repl = ur' %s="%s"' % (attr, newurl)
            content = re.sub(rx_abs_url, repl, content, count=1)
        return content

    def is_html_fragment(self, content):
        head = content[:500].strip().lower()
        return not (head.startswith('<!doctype ') or head.startswith('<html'))

    def must_be_included(self, path):
        return path in self.settings.get('INCLUDE', [])

    def must_be_filtered(self, path):
        filename = basename(path)
        return filename.startswith('.') or path in self.settings.get('FILTER', [])

    def must_filter_fragment(self, content):
        return self.settings.get('FILTER_PARTIALS') and self.is_html_fragment(content)

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
            if not path.endswith(TMPL_EXTS):
                continue

            if not self.must_be_included(path):
                if self.must_be_filtered(path):
                    continue
                content = self.render(path, self.settings)
                if self.must_filter_fragment(content):
                    continue

            fullpath = self.get_full_source_path(path)
            updated_at = get_updated_datetime(fullpath)
            index.append((path, updated_at))
        return index

    def send_file(self, path):
        fp = self.get_full_source_path(path)
        try:
            return send_file(fp)
        except IOError:
            return self.show_notfound(path)

    def render_page(self, path=None):
        path = self.normalize_path(path)

        if not path.endswith(TMPL_EXTS):
            return self.send_file(path)

        try:
            res = self.render(path, self.settings)
        except TemplateNotFound, e:
            return self.show_notfound(e)

        response = make_response(res)
        response.mimetype = self.guess_mimetype(self.get_real_fn(path))
        return response

    def _make__index(self, path):
        index = self.get_pages_index()
        context = self.settings.copy()
        context['index'] = index
        return self.render(path, context)

    def show__index_txt(self):
        path = '_index.txt'
        content = self._make__index(path)
        resp = make_response(content)
        resp.mimetype = 'text/plain'
        return resp

    def build__index_txt(self):
        path = '_index.txt'
        self.print_build_message(path)
        content = self._make__index(path)
        bp = self.get_full_build_path(path)
        create_file(bp, content)

    def show__index(self):
        path = '_index.html'
        content = self._make__index(path)
        resp = make_response(content)
        resp.mimetype = 'text/html'
        return resp

    def build__index(self):
        path = '_index.html'
        self.print_build_message(path)
        content = self._make__index(path)
        bp = self.get_full_build_path(path)
        create_file(bp, content)

    def print_build_message(self, path):
        print ' ', to_unicode(self.remove_template_ext(path))

    def build_page(self, path):
        sp = self.get_full_source_path(path)
        bp = self.get_full_build_path(path)
        make_dirs(dirname(bp))

        if not path.endswith(TMPL_EXTS):
            if self.must_be_filtered(path):
                return
            self.print_build_message(path)
            return copy_if_updated(sp, bp)

        content = u''
        if not self.must_be_included(path):
            if self.must_be_filtered(path):
                return
            content = self.render(path, self.settings)
            if self.must_filter_fragment(content):
                return

        self.print_build_message(path)
        bp = self.remove_template_ext(bp)
        if bp.endswith('.html'):
            content = self.make_absolute_urls_relative(content, path)

        create_file(bp, content)   

    def run(self, host=None, port=None):
        if not exists(self.source_dir):
            print SOURCE_NOT_FOUND
            return
        return self.server.run(host, port)
    
    def build(self):
        pages = self.get_pages_list()
        print u'Building...\n'
        for path in pages:
            self.build_page(path)
        self.build__index()
        self.build__index_txt()
        print u'\nDone.'

    def show_notfound(self, path):
        context = self.settings.copy()
        context['path'] = path
        res = self.render('_notfound.html', context)
        return make_response(res, HTTP_NOT_FOUND)

    def get_test_client(self):
        self.app.testing = True
        host = self.settings.get('host', DEFAULT_HOST)
        port = self.settings.get('port', DEFAULT_PORT)
        self.app.config['SERVER_NAME'] = '%s:%s' % (host, port)
        return self.app.test_client()

