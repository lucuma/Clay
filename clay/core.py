#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Clay

A rapid prototyping tool


Copyright © 2011 by Lúcuma labs (http://lucumalabs.com).
Coded by Juan-Pablo Scaletti <juanpablo@lucumalabs.com>.
MIT License. (http://www.opensource.org/licenses/mit-license.php).
"""
import mimetypes
import os

from jinja2 import PackageLoader, ChoiceLoader, FileSystemLoader
from shake import Shake, Settings, Render, Rule, NotFound, TemplateNotFound

from .static import render_static_file, make_static_file
from .utils import (walk_dir, make_dirs, make_file,
    get_processed_regex, replace_processed_names)


STATIC_DIR = 'static'
VIEWS_DIR = 'views'
BUILD_DIR = 'build'
VIEWS_INDEX = '_index.html'

default_settings = {
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
        self.static_dir = make_dirs(base_dir, STATIC_DIR)
        self.views_dir = make_dirs(base_dir, VIEWS_DIR)
        self.build_dir = os.path.join(base_dir, BUILD_DIR)
        
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
        
        return render_static_file(request, static_abspath)
    
    def run(self, host=None, port=None):
        host = host or self.settings.host
        port = port or self.settings.port
        return self.app.run(host, port)
    
    def make(self):
        """Generates a static version of the site.
        """
        processed_files = self._make_static()
        self._make_views(processed_files)
        print '\nDone!\n'
    
    def _make_views(self, processed_files):
        print '\nGenerating views...\n', '-' * 20
        rx_processed = get_processed_regex(processed_files)
        views_list = []

        def callback(relpath):
            vn = relpath.decode('utf8')
            # print vn
            views_list.append(vn)

            content = self.render.to_string(relpath, context_make)
            content = replace_processed_names(content, rx_processed)
            filepath = make_dirs(self.build_dir, relpath)
            make_file(filepath, content)
        
        walk_dir(self.views_dir, callback)
        self._make_views_list(views_list)
    
    def _make_views_list(self, views):
        print '\nMaking views list...\n', '-' * 20

        ignore = self.settings.views_list_ignore
        ignore.append(VIEWS_INDEX)
        views = [v for v in views if v not in ignore]
        context_make['views'] = views

        content = self.render.to_string(VIEWS_INDEX, context_make)
        final_path = make_dirs(self.build_dir, VIEWS_INDEX)
        make_file(final_path, content)
    
    def _make_static(self):
        print '\nProcessing static files...\n', '-' * 20
        processed_files = []

        def callback(relpath):
            filepath = make_dirs(self.static_dir, relpath)
            file_tuple = make_static_file(filepath)
            if file_tuple:
                processed_files.append(file_tuple)
        
        walk_dir(self.static_dir, callback)
        self._make_static_symlink()
        return processed_files
    
    def _make_static_symlink(self):
        make_dirs(self.build_dir, '')
        if os.symlink:
            _old = os.getcwd()
            os.chdir(self.build_dir)
            try:
                os.symlink(self.static_dir, STATIC_DIR)
            except (OSError), e:
                pass
            os.chdir(_old)
    
    def not_found(self):
        raise NotFound

    def _get_urls(self):
        return [
            Rule('/', self.render_view),
            Rule('/favicon.ico', redirect_to='/static/favicon.ico'),
            Rule('/static/<path:static_path>', self.render_static),
            Rule('/<path:view_path>', self.render_view),
        ]

