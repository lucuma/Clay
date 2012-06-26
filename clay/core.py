# -*- coding: utf-8 -*-
"""
# Clay.core

Main file

"""
from __future__ import absolute_import

import glob
import mimetypes
import os
import socket

from jinja2 import (PackageLoader, ChoiceLoader, FileSystemLoader)
from jinja2.exceptions import TemplateSyntaxError
from shake import (Shake, Settings, Render, Rule, NotFound, send_file,
    Response)

from . import utils, config
from . import p_scss, p_less, p_markdown, p_coffee
from . import pp_pygments, pp_typogrify


class Clay(object):

    def __init__(self, base_dir, settings=None, source_dir=config.SOURCE_DIR):
        if os.path.isfile(base_dir):
            base_dir = os.path.abspath(os.path.dirname(base_dir))
        self.base_dir = base_dir
        self.source_dir = utils.make_dirs(base_dir, source_dir)
        self.build_dir = os.path.join(base_dir, config.BUILD_DIR)

        settings = settings or {}
        self.settings = Settings(config.default_settings, settings,
            case_insensitive=True)

        theme_prefix = self.settings.get('theme_prefix', '').rstrip('/')
        if theme_prefix:
            theme_prefix += '/'
        self.settings['theme_prefix'] = theme_prefix

        views_ignore = self.settings.get('views_ignore', [])
        self.settings['views_ignore'] = tuple(views_ignore)

        self.app = Shake(config.app_settings)
        self._make_render()
        self._enable_pre_processors()
        self._add_urls()

    def _make_render(self):
        loader = ChoiceLoader([
            FileSystemLoader(self.source_dir),
            PackageLoader('clay', config.SOURCE_DIR),
        ])
        self.render = Render(loader=loader)
        self.render.set_filter('json', utils.filter_to_json)

    def _enable_pre_processors(self):
        ext_trans = {}
        processors = self.settings.pre_processors

        for name in processors:
            pr = globals().get('p_' + name)
            if pr and pr.enabled:
                pr.add_extensions(self)
                for ext in pr.extensions_in:
                    ext_trans[ext] = pr.extension_out

        self.ext_trans = ext_trans

    def _add_urls(self):
        self.app.add_urls([
            Rule('/', self.render_view),
            Rule('/<path:path>', self.render_view),
        ])

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

    def _translate_ext(self, old_ext):
        return self.ext_trans.get(old_ext, old_ext)

    def _get_alternative(self, path):
        path = path.strip('/')
        fname, ext = os.path.splitext(path)
        fullpath = os.path.join(config.DEFAULT_TEMPLATES, path)
        if os.path.exists(fullpath):
            return ext, path, fullpath
        
        if path != 'index.html':
            return None, None, None

        pdir = os.path.join(self.source_dir, fname + '.*')
        files = glob.glob(pdir)
        if files:
            fullpath = files[0]
            path = fullpath.replace(self.source_dir, '')
            _, ext = os.path.splitext(path)
            return ext, path, fullpath

        return None, None, None

    def _post_process(self, html):
        html = utils.to_unicode(html)
        processors = self.settings.post_processors

        for name in processors:
            pp = globals().get('pp_' + name)
            if pp and pp.enabled:
                html = pp.process(html)

        return html

    def run(self, host=None, port=None):
        host = host if host is not None else self.settings.HOST
        port = port if port is not None else self.settings.PORT
        try:
            port = int(port)
        except Exception:
            port = self.settings.PORT
        ips = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
            if not ip.startswith("127.")][:1]
        if ips:
            print ' * Your local IP is:', ips[0]
        try:
            self.app.run(host=host, port=port)
        except socket.error, e:
            print e

    def build(self):
        """Generates a static version of the site.
        """
        print '\nGenerating views...\n', '-' * 20
        self.build_views()
        print '\nDone!\n'

    def test_client(self):
        return self.app.test_client()

    def render_view(self, request, path=''):
        """Default controller.
        Render the template at `path` guessing it's mimetype.
        """
        path = self._normalize_path(path)
        fn, ext = os.path.splitext(path)
        real_ext = self._translate_ext(ext)
        fullpath = os.path.join(self.source_dir, path.lstrip('/'))

        if not os.path.exists(fullpath):
            ext, path, fullpath = self._get_alternative(path)
            if not fullpath:
                return self.not_found()

        plain_text_exts = self.settings.plain_text
        if ext in plain_text_exts or utils.is_binary(fullpath):
            return send_file(request, fullpath)

        try:
            resp = self.render(path, **self.settings)
        except TemplateSyntaxError, e:
            print '-- WARNING:', 'Syntax error while trying to process', \
                    utils.to_unicode(path), 'as a Jinja template.'
            source = utils.get_source(fullpath)
            resp = Response(source)
            print e

        if real_ext == '.html':
            resp.data = self._post_process(resp.data)

        resp.mimetype = mimetypes.guess_type('a' + real_ext)[0] or 'text/plain'
        return resp

    def build_views(self):
        processed = []
        views = []
        views_ignore = self.settings.views_ignore
        theme_prefix = self.settings.theme_prefix

        def callback(relpath_in):
            if relpath_in.endswith(views_ignore):
                return
            fn, ext = os.path.splitext(relpath_in)
            real_ext = self._translate_ext(ext)
            relpath_in_real = '%s%s' % (fn, real_ext)
            relpath_out = relpath_in_real
            if theme_prefix and not relpath_out.startswith(theme_prefix):
                relpath_out = os.path.join(theme_prefix, relpath_out)
            print relpath_out

            path_in = os.path.join(self.source_dir, relpath_in)
            path_out = utils.make_dirs(self.build_dir, relpath_out)

            plain_text_exts = self.settings.plain_text
            if ext in plain_text_exts or utils.is_binary(path_in):
                return utils.copy_if_has_change(path_in, path_out)

            try:
                content = self.render.to_string(relpath_in.replace('\\', '/'), **self.settings)
            except TemplateSyntaxError:
                print '-- WARNING:', 'Syntax error while trying to process', \
                    utils.to_unicode(relpath_in), 'as a Jinja template.'
                content = utils.get_source(path_in)
            
            if real_ext != ext:
                processed.append([relpath_in, relpath_in_real])

            if real_ext == '.html':
                content = self._post_process(content)
                return views.append([relpath_in, path_out, content])

            utils.make_file(path_out, content)
            return
        
        utils.walk_dir(self.source_dir, callback, config.IGNORE)
        rx_processed = utils.get_processed_regex(processed)
        views_list = []

        for relpath_in, path_out, content in views:
            content = utils.absolute_to_relative(content, relpath_in,
                theme_prefix)
            content = utils.replace_processed_names(content, rx_processed)
            utils.make_file(path_out, content)
            views_list.append(relpath_in.decode('utf8'))
        
        self.build_views_list(views_list)

    def build_views_list(self, views):
        ignore = self.settings.views_list_ignore
        ignore.append(config.VIEWS_INDEX)
        real_views = []

        for v in views:
            if v in ignore or v.startswith(config.IGNORE):
                continue
            mdate = utils.get_file_mdate(os.path.join(self.source_dir, v))
            fn, ext = os.path.splitext(v)
            real_ext = self._translate_ext(ext)
            v = '%s%s' % (fn, real_ext)
            real_views.append((v, ' / '.join(v.split('/')), mdate))
        
        content = self.render.to_string(config.VIEWS_INDEX, views=real_views)
        relpath = os.path.join(self.settings.theme_prefix, config.VIEWS_INDEX)
        print relpath
        final_path = utils.make_dirs(self.build_dir, relpath)
        utils.make_file(final_path, content)

    def not_found(self):
        resp = self.render('notfound.html')
        resp.status_code = 404
        resp.mimetype = 'text/html'
        return resp

