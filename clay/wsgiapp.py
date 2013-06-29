# -*- coding: utf-8 -*-
from datetime import datetime
from os.path import basename

from flask import (Flask, has_request_context, render_template, make_response, send_file)
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from jinja2.exceptions import TemplateNotFound

from .tglobals import active, IncludeWith


APP_NAME = 'clay'

TEMPLATE_GLOBALS = {
    'CLAY_URL': 'http://lucuma.github.com/Clay',
    'active': active,
    'now': datetime.utcnow(),
    'dir': dir,
    'enumerate': enumerate,
    'map': map,
    'zip': zip,
}


class WSGIApplication(Flask):

    def __init__(self, source_dir):
        super(WSGIApplication, self).__init__(
            APP_NAME, template_folder=source_dir, static_folder=None)
        self.jinja_loader = get_jinja_loader(source_dir)
        self.jinja_options = get_jinja_options()
        self.context_processor(lambda: TEMPLATE_GLOBALS)
        self.debug = True

    def get_test_client(self, host, port):
        self.testing = True
        self.config['SERVER_NAME'] = '%s:%s' % (host, port)
        return self.test_client()

    def render_template(self, path, context, host, port):
        if has_request_context():
            return render_template(path, **context)

        with self.test_request_context(
                '/' + path, method='GET',
                base_url='http://%s:%s' % (host, port)):
            return render_template(path, **context)

    def response(self, content, status=200, mimetype='text/plain'):
        resp = make_response(content, status)
        resp.mimetype = mimetype
        return resp

    def send_file(self, *args, **kwargs):
        return send_file(*args, **kwargs)


def get_jinja_loader(source_dir):
    return ChoiceLoader([
        FileSystemLoader(source_dir),
        PackageLoader('clay', basename(source_dir)),
    ])


def get_jinja_options():
    return {
        'autoescape': True,
        'extensions': ['jinja2.ext.with_', IncludeWith]
    }
