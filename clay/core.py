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

from . import static, utils


STATIC_DIR = 'static'
VIEWS_DIR = 'views'
BUILD_DIR = 'build'

VIEWS_INDEX = '_index.html'

IGNORE = ('.', '_')


default_settings = {
    'views_list_ignore': [],

    # CoffeeScript settings
    'coffee': {
        # Compile without a top-level function wrapper
        'bare': False
    },

    'host': '0.0.0.0',
    'port': 5000,
}

context_run = {
    'STATIC': '/' + STATIC_DIR,
}

context_build = {
    'STATIC': STATIC_DIR,
}


class Clay(object):

    def __init__(self, base_dir, settings=None):
        if os.path.isfile(base_dir):
            base_dir = os.path.dirname(base_dir)
        self.base_dir = base_dir
        self.static_dir = utils.make_dirs(base_dir, STATIC_DIR)
        self.views_dir = utils.make_dirs(base_dir, VIEWS_DIR)
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
        
        return static.render(request, static_abspath, self.settings)
    
    def run(self, host=None, port=None):
        host = host or self.settings.host
        port = port or self.settings.port
        return self.app.run(host, port)
    
    def build(self):
        """Generates a static version of the site.
        """
        processed_files = self._make_static()
        self._make_views(processed_files)
        print '\nDone!\n'
    
    def _make_views(self, processed_files):
        print '\nGenerating views...\n', '-' * 20
        rx_processed = utils.get_processed_regex(processed_files)
        views_list = []

        def callback(relpath):
            uv = relpath.decode('utf8')
            print uv
            views_list.append(uv)
            content = self.render.to_string(relpath, context_build)
            content = utils.replace_processed_names(content, rx_processed)
            filepath = utils.make_dirs(self.build_dir, relpath)
            utils.make_file(filepath, content)
        
        utils.walk_dir(self.views_dir, callback, IGNORE)
        self._make_views_list(views_list)
    
    def _make_views_list(self, views):
        ignore = self.settings.views_list_ignore
        ignore.append(VIEWS_INDEX)

        views = [
            (
                v,
                ' / '.join(v.split('/')),
                utils.get_file_mdate(os.path.join(self.views_dir, v))
            ) \
            for v in views \
                if v not in ignore and not v.startswith(IGNORE)
            ]
        context_build['views'] = views

        content = self.render.to_string(VIEWS_INDEX, context_build)
        final_path = utils.make_dirs(self.build_dir, VIEWS_INDEX)
        utils.make_file(final_path, content)
    
    def _make_static(self):
        print '\nProcessing static files...\n', '-' * 20
        processed_files = []

        def callback(relpath):
            filepath = utils.make_dirs(self.static_dir, relpath)
            file_tuple = static.build(filepath, self.settings)
            if file_tuple:
                processed_files.append(file_tuple)
        
        utils.walk_dir(self.static_dir, callback, IGNORE)
        self._make_static_symlink()
        return processed_files
    
    def _make_static_symlink(self):
        utils.make_dirs(self.build_dir, '')
        if os.symlink:
            _old = os.getcwd()
            os.chdir(self.build_dir)
            try:
                os.symlink(self.static_dir, STATIC_DIR)
            except (OSError), e:
                pass
            os.chdir(_old)
    
    def not_found(self):
        resp = self.render('notfound.html')
        resp.status_code = 404
        return resp
    
    def _get_urls(self):
        return [
            Rule('/', self.render_view),
            Rule('/favicon.ico', redirect_to='/static/favicon.ico'),
            Rule('/static/<path:static_path>', self.render_static),
            Rule('/<path:view_path>', self.render_view),
        ]

