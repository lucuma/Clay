# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime
import socket
import sys

from cherrypy import wsgiserver


ALL_HOSTS = '0.0.0.0'
DEFAULT_HOST = ALL_HOSTS
DEFAULT_PORT = 8080
MAX_PORT_DELTA = 10

WELCOME = u' # Clay (by Lucuma labs)\n'
ADDRINUSE = u' ---- Address already in use. Trying another port...'
RUNNING_ON = u' * Running on http://%s:%s'
HOW_TO_QUIT = u' -- Quit the server with Ctrl+C --\n'

HTTPMSG = '500 Internal Error'


class Server(object):

    def __init__(self, clay):
        self.clay = clay
        app = RequestLogger(clay.app)
        self.dispatcher = wsgiserver.WSGIPathInfoDispatcher({'/': app})

    def run(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        port = port or self.clay.settings.get('port', DEFAULT_PORT)
        host = host or self.clay.settings.get('host', DEFAULT_HOST)
        max_port = port + MAX_PORT_DELTA
        print(WELCOME)
        return self._testrun(host, port, max_port)

    def _testrun(self, host, current_port, max_port):
        self.print_help_msg(host, current_port)
        try:
            self._run_wsgi_server(host, current_port)
        except socket.error:
            current_port += 1
            if current_port > max_port:
                return
            print(ADDRINUSE)
            self._testrun(host, current_port, max_port)
        except KeyboardInterrupt:
            self.stop()
        return host, current_port

    def _run_wsgi_server(self, host, port):
        self.server = self._get_wsgi_server(host, port)
        self.start()

    def _get_wsgi_server(self, host, port):
        return wsgiserver.CherryPyWSGIServer(
            (host, port),
            wsgi_app=self.dispatcher
        )

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def print_help_msg(self, host, port):
        if host == ALL_HOSTS:
            print(RUNNING_ON % ('localhost', port))
            local_ip = get_local_ip()
            if local_ip:
                print(RUNNING_ON % (local_ip, port))
        print(HOW_TO_QUIT)


class RequestLogger(object):

    def __init__(self, application, **kw):
        self.application = application

    def log_request(self, environ, now=None):
        now = now or datetime.now()
        msg = [
            ' ',
            now.strftime('%H:%M:%S'), ' | ',
            environ.get('REMOTE_ADDR', '?'), '  ',
            environ.get('REQUEST_URI', ''), '  ',
            '(', environ.get('REQUEST_METHOD', ''), ')',
        ]
        msg = ''.join(msg)
        print(msg)

    def __call__(self, environ, start_response):
        self.log_request(environ)
        try:
            return self.application(environ, start_response)
        except Exception:
            start_response(HTTPMSG, [('Content-type', 'text/plain')], sys.exc_info())
            raise


def get_local_ip():
    try:
        interfaces = socket.gethostbyname_ex(socket.gethostname())[-1]
    except socket.gaierror:
        return
    for ip in interfaces:
        if ip.startswith('192.'):
            return ip
