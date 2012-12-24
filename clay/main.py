# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime
import mimetypes
import os
from os.path import (isfile, isdir, dirname, join, splitext, split, exists,
    relpath, sep)
import re
import socket

from flask import (Flask, request, has_request_context, render_template,
    send_file, make_response, abort)
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
import yaml

from .helpers import (read_content, make_dirs, create_file,
    copy_if_updated, get_updated_datetime)
from .tglobals import link_to, to_unicode


SOURCE_DIRNAME = 'source'
BUILD_DIRNAME = 'build'
TMPL_EXTS = ('.html', '.tmpl')
RX_TMPL = re.compile(r'\.tmpl$')

HTTP_NOT_FOUND = 404

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080

WELCOME = """--- Clay - A rapid prototyping tool by Lucuma labs ---"""

SOURCE_NOT_FOUND_HELP = """We couldn't found a "%s" dir.
Are you sure you're in the correct folder? """ % SOURCE_DIRNAME

rx_abs_url = re.compile(r'\s(src|href)=[\'"](\/(?:[a-z0-9][^\'"]*)?)[\'"]',
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
        _, filename = split(path)
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
            raise abort(HTTP_NOT_FOUND)

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
        self.print_build_message(path)
        
        index = self.get_pages_index()
        bp = self.get_full_build_path(path)
        context = self.settings.copy()
        context['index'] = index
        content = self.render(path, context)
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

    def print_welcome_msg(self):
        print WELCOME

    def print_help_msg(self, host, port):
        print ' - Quit the server with Ctrl+C -'
        if host == '0.0.0.0':
            ips = [ip 
                for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                if not ip.startswith("127.")
            ][:1]
            if ips:
                print ' * Running on http://%s:%s' % (ips[0], port)

    def run(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        if not exists(self.source_dir):
            print SOURCE_NOT_FOUND_HELP
            return

        config = self.get_run_config(host, port)
        self.print_welcome_msg()
        self.print_help_msg(config['host'], config['port'])
        try:
            return self.app.run(**config)
        except socket.error, e:
            print e
    
    def build(self):
        pages = self.get_pages_list()
        print u'Building...\n'
        for path in pages:
            self.build_page(path)
        self.build__index()
        print u'\nDone.'

    def get_test_client(self):
        self.app.testing = True
        return self.app.test_client()

