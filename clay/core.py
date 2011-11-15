#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Clay

A rapid prototyping tool


Copyright © 2011 by Lúcuma labs (http://lucumalabs.com).
Coded by Juan-Pablo Scaletti <juanpablo@lucumalabs.com>.
MIT License. (http://www.opensource.org/licenses/mit-license.php).
"""
import errno
import io
import mimetypes
import os
import sys

from jinja2 import PackageLoader, ChoiceLoader, FileSystemLoader
from shake import (Shake, Settings, Render, Rule, send_file,
    NotFound, TemplateNotFound)


STATIC_DIR = 'static'
VIEWS_DIR = 'views'
BUILD_DIR = 'build'

default_settings = {
    'views_list': '_index.html',
    'views_list_ignore': [],
    'host': '0.0.0.0',
    'port': 5000,
}

context_run = {
    'STATIC': '/' + STATIC_DIR,
}

context_make = {
    'STATIC': STATIC_DIR,
}


class Clay(object):

    def __init__(self, base_dir, settings=None):
        if os.path.isfile(base_dir):
            base_dir = os.path.dirname(base_dir)
        self.base_dir = base_dir
        self.static_dir = os.path.join(base_dir, STATIC_DIR)
        self.views_dir = os.path.join(base_dir, VIEWS_DIR)
        self.build_dir = os.path.join(base_dir, BUILD_DIR)

        self._make_dirs(self.static_dir)
        self._make_dirs(self.views_dir)
        
        self.settings = Settings(default_settings, settings,
            case_insensitive=True)
        self.app = Shake(self._get_urls())

        loader = ChoiceLoader([
            FileSystemLoader(self.views_dir),
            PackageLoader('clay', 'views'),
        ])
        self.render = Render(loader=loader)
    
    def test_client(self):
        return self.app.test_client()
    
    def render_view(self, request, view_path=''):
        """Default controller.
        Render the template at `view_path` guessing it's mimetype.
        """
        if '..' in view_path:
            return self.not_found()
        view_path = view_path.strip('/')
        is_dir = os.path.isdir(os.path.join(self.views_dir, view_path))
        if is_dir:
            view_path += '/'
        if not view_path or is_dir:
            view_path += 'index.html'
        
        mime = mimetypes.guess_type(view_path)[0] or 'text/plain'
        try:
            return self.render(view_path, context_run, mimetype=mime)
        except TemplateNotFound:
            return self.not_found()
    
    def render_static(self, request, static_path):
        if '..' in static_path:
            return self.not_found()
        static_path = static_path.strip('/')
        static_abspath = os.path.join(self.static_dir, static_path)
        if not os.path.isfile(static_abspath):
            return self.not_found()
        #TODO: Static file processing
        return send_file(request, static_abspath)
    
    def run(self, host=None, port=None):
        host = host or self.settings.host
        port = port or self.settings.port
        return self.app.run(host, port)
    
    def make(self):
        """Generates a static version of the site.
        """
        self._make_views()
        self._make_static()
        print '\nDone!\n'
    
    def _make_views(self):
        print '\nGenerating views...\n', '-' * 20
        views_list = []

        for folder, subs, files in os.walk(self.views_dir):
            ffolder = os.path.relpath(folder, self.views_dir)
            for filename in files:
                if filename.startswith('.'):
                    continue
                filepath = os.path.join(ffolder, filename) \
                    .lstrip('.').lstrip('/')
                vn = filepath.decode('utf8')
                print vn
                views_list.append(vn)

                content = self.render.to_string(filepath, context_make)
                content = content.encode('utf8')
                final_path = self._make_dirs(self.build_dir, filepath)
                with io.open(final_path, 'w+b') as f:
                    f.write(content)
        
        self._make_views_list(views_list)
    
    def _make_views_list(self, views):
        print '\nMaking views list...\n', '-' * 20
        tmpl_name = self.settings.views_list

        ignore = self.settings.views_list_ignore
        ignore.append(tmpl_name)
        views = [v for v in views if v not in ignore]
        context_make['views'] = views

        content = self.render.to_string(tmpl_name, context_make)
        
        content = content.encode('utf8')
        final_path = self._make_dirs(self.build_dir, tmpl_name)
        with io.open(final_path, 'w+b') as f:
            f.write(content)
    
    def _make_static(self):
        print '\nProcessing static files...\n', '-' * 20
        pass
        if os.symlink:
            _old = os.getcwd()
            os.chdir(self.build_dir)
            try:
                os.symlink(self.static_dir, STATIC_DIR)
            except (OSError), e:
                pass
            os.chdir(_old)
    
    def _make_dirs(self, *lpath):
        path = os.path.join(*lpath)
        try:
            os.makedirs(os.path.dirname(path))
        except (OSError), e:
            if e.errno != errno.EEXIST:
                raise
        return path
    
    def not_found(self):
        raise NotFound

    def _get_urls(self):
        return [
            Rule('/', self.render_view),
            Rule('/favicon.ico', redirect_to='/static/favicon.ico'),
            Rule('/static/<path:static_path>', self.render_static),
            Rule('/<path:view_path>', self.render_view),
        ]

