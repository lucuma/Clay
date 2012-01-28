# -*- coding: utf-8 -*-
"""
    # Clay.core

    Main file

"""
from __future__ import absolute_import

import mimetypes
import os
import shutil

from shake import (Shake, Settings, Rule, NotFound,
    TemplateNotFound, Response, send_file)

from . import utils
from .config import *
from .render import Render


class Clay(object):

    def __init__(self, base_dir, settings=None, source_dir=SOURCE_DIR):
        if os.path.isfile(base_dir):
            base_dir = os.path.abspath(os.path.dirname(base_dir))
        self.base_dir = base_dir
        self.settings = settings
        self.source_dir = utils.make_dirs(base_dir, source_dir)
        self.build_dir = os.path.join(base_dir, BUILD_DIR)

        self.settings = Settings(default_settings, settings,
            case_insensitive=True)
        
        self.app = Shake(self._get_urls())
        self.render = Render(self.source_dir, self.settings)
    
    def run(self, host=None, port=None):
        host = host or self.settings.host
        port = port or self.settings.port
        return self.app.run(host, port)
    
    def build(self):
        """Generates a static version of the site.
        """
        print '\nGenerating views...\n', '-' * 20
        self.build_views()
        print '\nDone!\n'
    
    def test_client(self):
        return self.app.test_client()
    
    def _get_urls(self):
        return [
            Rule('/', self.render_view),
            Rule('/<path:path>', self.render_view),
        ]
    
    def _normalize_path(self, path):
        if '..' in path:
            return self.not_found()
        path = path.strip('/')
        is_dir = os.path.isdir(os.path.join(self.source_dir, path))
        if is_dir:
            path += '/'
        if not path or is_dir:
            path += 'index.html'
        return path
    
    def render_view(self, request, path=''):
        """Default controller.
        Render the template at `path` guessing it's mimetype.
        """
        path = self._normalize_path(path)
        try:
            content, ext = self.render(path)
            mimetype = mimetypes.guess_type('a' + ext)[0] or 'text/plain'
        except TemplateNotFound:
            return self.not_found()
        if content:
            return Response(content, mimetype=mimetype)
        
        fullpath = os.path.join(self.source_dir, path)
        if not os.path.isfile(fullpath):
            return self.not_found() 
        return send_file(request, fullpath)
    
    def build_views(self):
        processed = []
        views = []

        def callback(relpath_in):
            print relpath_in
            fn, old_ext = os.path.splitext(relpath_in)
            content, ext = self.render(relpath_in)
            relpath_out = '%s%s' % (fn, ext)
            path_in = os.path.join(self.source_dir, relpath_in)
            path_out = utils.make_dirs(self.build_dir, relpath_out)

            if not content:
                return shutil.copy2(path_in, path_out)
            if ext == '.html':
                return views.append([relpath_in, path_out, content])
            if ext != old_ext:
                processed.append([relpath_in, relpath_out])
            utils.make_file(path_out, content)
            return
        
        utils.walk_dir(self.source_dir, callback, IGNORE)
        rx_processed = utils.get_processed_regex(processed)
        views_list = []

        for relpath_in, path_out, content in views:
            content = utils.absolute_to_relative(content, relpath_in)
            content = utils.replace_processed_names(content, rx_processed)
            utils.make_file(path_out, content)
            views_list.append(relpath_in.decode('utf8'))
        
        self.build_views_list(views_list)
    
    def build_views_list(self, views):
        ignore = self.settings.views_list_ignore
        ignore.append(VIEWS_INDEX)

        views = [
            (
                v,
                ' / '.join(v.split('/')),
                utils.get_file_mdate(os.path.join(self.source_dir, v)),
            ) \
            for v in views \
                if v not in ignore and not v.startswith(IGNORE)
            ]
        content, mimetype = self.render(VIEWS_INDEX, views=views)
        final_path = utils.make_dirs(self.build_dir, VIEWS_INDEX)
        utils.make_file(final_path, content)
    
    def not_found(self):
        content, ext = self.render('notfound.html')
        resp = Response(content)
        resp.status_code = 404
        resp.mimetype = 'text/html'
        return resp

