# -*- coding: utf-8 -*-
from __future__ import print_function

from fnmatch import fnmatch
import mimetypes
import os
from os.path import (
    isfile, isdir, dirname, join, splitext, basename, exists,
    relpath, sep)
import re
import sys

import yaml

from .helpers import (
    to_unicode, read_content, make_dirs, create_file,
    copy_if_updated, get_updated_datetime, sort_paths_dirs_last)
from .server import Server, DEFAULT_HOST, DEFAULT_PORT
from .wsgiapp import WSGIApplication, TemplateNotFound
from functools import reduce


SOURCE_DIRNAME = 'source'
BUILD_DIRNAME = 'build'
TMPL_EXTS = ('.html', '.tmpl')
RX_TMPL = re.compile(r'\.tmpl$')

HTTP_NOT_FOUND = 404

SOURCE_NOT_FOUND = u"""We couldn't found a "%s" dir.
Check if you're in the correct folder""" % SOURCE_DIRNAME

rx_abs_url = re.compile(
    r'\s(src|href|data-[a-z0-9_-]+)\s*=\s*[\'"](\/(?:[a-z0-9_-][^\'"]*)?)[\'"]',
    re.UNICODE | re.IGNORECASE)


class Clay(object):

    _cached_pages_list = None

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
        app = WSGIApplication(self.source_dir)
        self.set_urls(app)
        return app

    def set_urls(self, app):
        app.add_url_rule('/', 'page', self.render_page)
        app.add_url_rule('/<path:path>', 'page', self.render_page)
        app.add_url_rule('/_index.html', 'index', self.show__index)
        app.add_url_rule('/_index.txt', 'index_txt', self.show__index_txt)

    def load_settings_from_file(self):
        if isfile(self.settings_path):
            source = read_content(self.settings_path)
            st = yaml.safe_load(source)
            self.settings.update(st)

    def render(self, path, context):
        host = self.settings.get('host', DEFAULT_HOST)
        port = self.settings.get('port', DEFAULT_PORT)
        return self.app.render_template(path, context, host, port)

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
        patterns = self.settings.get('INCLUDE', []) or []
        return reduce(lambda r, pattern: r or
                      fnmatch(path, pattern), patterns, False)

    def must_be_filtered(self, path):
        filename = basename(path)
        patterns = self.settings.get('FILTER', []) or []
        return (filename.startswith('.') or
                reduce(lambda r, pattern: r or
                fnmatch(path, pattern), patterns, False))

    def must_filter_fragment(self, content):
        return bool(self.settings.get('FILTER_PARTIALS', True)) \
            and self.is_html_fragment(content)

    def get_pages_list(self, pattern=None):
        if self._cached_pages_list:
            return self._cached_pages_list
        pages = []
        for folder, subs, files in os.walk(self.source_dir):
            rel = self.get_relpath(folder)
            for filename in files:
                path = join(rel, filename)
                if not pattern or fnmatch(path, pattern):
                    pages.append(path)
        self._cached_pages_list = pages
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
        return sort_paths_dirs_last(index)

    def send_file(self, path):
        fp = self.get_full_source_path(path)
        try:
            return self.app.send_file(fp)
        except IOError:
            return self.show_notfound(path)

    def render_page(self, path=None):
        path = self.normalize_path(path)

        if not path.endswith(TMPL_EXTS):
            return self.send_file(path)

        try:
            content = self.render(path, self.settings)
        except TemplateNotFound as e:
            return self.show_notfound(e)

        mimetype = self.guess_mimetype(self.get_real_fn(path))
        return self.app.response(content, mimetype=mimetype)

    def _make__index(self, path):
        index = self.get_pages_index()
        context = self.settings.copy()
        context['index'] = index
        return self.render(path, context)

    def show__index_txt(self):
        path = '_index.txt'
        content = self._make__index(path)
        return self.app.response(content, mimetype='text/plain')

    def build__index_txt(self):
        path = '_index.txt'
        self.print_build_message(path)
        content = self._make__index(path)
        bp = self.get_full_build_path(path)
        create_file(bp, content)

    def show__index(self):
        path = '_index.html'
        content = self._make__index(path)
        return self.app.response(content, mimetype='text/html')

    def build__index(self):
        path = '_index.html'
        self.print_build_message(path)
        content = self._make__index(path)
        bp = self.get_full_build_path(path)
        create_file(bp, content)

    def print_build_message(self, path):
        print(' ', to_unicode(self.remove_template_ext(path)))

    def build_page(self, path):
        sp = self.get_full_source_path(path)
        bp = self.get_full_build_path(path)
        make_dirs(dirname(bp))

        if not path.endswith(TMPL_EXTS):
            if self.must_be_filtered(path):
                return
            self.print_build_message(path)
            return copy_if_updated(sp, bp)

        must_be_included = self.must_be_included(path)

        if self.must_be_filtered(path) and not must_be_included:
            return

        content = self.render(path, self.settings)
        if self.must_filter_fragment(content) and not must_be_included:
            return

        self.print_build_message(path)
        bp = self.remove_template_ext(bp)
        if bp.endswith('.html'):
            content = self.make_absolute_urls_relative(content, path)

        create_file(bp, content)

    def run(self, host=None, port=None):
        if not exists(self.source_dir):
            print(SOURCE_NOT_FOUND)
            return
        return self.server.run(host, port)

    def build(self, pattern=None):
        self._cached_pages_list = None
        pages = self.get_pages_list(pattern)
        print('Building...\n')
        for path in pages:
            self.build_page(path)
        self.build__index()
        self.build__index_txt()
        print('\nDone.')

    def show_notfound(self, path):
        context = self.settings.copy()
        context['path'] = path
        res = self.render('_notfound.html', context)
        return self.app.response(res, status=HTTP_NOT_FOUND, mimetype='text/html')

    def get_test_client(self):
        host = self.settings.get('host', DEFAULT_HOST)
        port = self.settings.get('port', DEFAULT_PORT)
        return self.app.get_test_client(host, port)
