from datetime import datetime
from urllib.parse import quote
import logging
import mimetypes
import sys

from gevent import pywsgi
from whitenoise import WhiteNoise

from .request import Request
from .utils import make_active_helper

logger = logging.getLogger()


class WSGIApp(object):
    def __init__(self, clay):
        self.clay = clay

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response):
        request = Request(environ)
        body, status, headers = self.call(request)
        start_response(status, headers)
        return [body.encode("utf8")]

    def call(self, request):
        path = request.path
        if not self.clay.file_exists(path):
            if path == "favicon.ico":
                return self.redirect_to("static/" + path)
            else:
                return self.not_found(request)
        active = make_active_helper(request)
        body = self.clay.render_file(path, request=request, active=active)
        mime = mimetypes.guess_type(path)[0] or "text/plain"
        response_headers = [
            ("Content-Type", mime),
            ("Content-Length", str(len(body)))
        ]
        return body, "200 OK", response_headers

    def run(self, host, port):
        set_logger()
        server = pywsgi.WSGIServer((host, port), self.wsgi, handler_class=ClayHandler)
        display_running_message(host, port)
        try:
            return server.serve_forever()
        except KeyboardInterrupt:
            print("\n Goodbye!\n")

    def not_found(self, request):
        mime = "text/plain"
        body = f"File {request.path} not found."
        active = make_active_helper(request)
        for path in ["not-found.html", "_notfound.html"]:
            if self.clay.file_exists(path):
                mime = "text/html"
                body = self.clay.render_file(path, request=request, active=active)
                break

        response_headers = [
            ("Content-Type", mime),
            ("Content-Length", str(len(body)))
        ]
        return body, "404 Not Found", response_headers

    def redirect_to(self, path):
        return "", "302 Found", [("Location", quote(path.encode("utf8")))]


class ClayHandler(pywsgi.WSGIHandler):
    STATUS_REPR = {"200": " ✔︎ ", "404": " ? ", "304": " = ", "500": "xxx"}

    def format_request(self):
        now = datetime.now()
        if isinstance(self.client_address, tuple):
            client_address = self.client_address[0]
        else:
            client_address = self.client_address
        status = self._orig_status.split()[0]
        status_repr = self.STATUS_REPR.get(status, status)

        return " {} {} -> {} {}".format(
            now.strftime("%H:%M:%S"),
            client_address or "?",
            status_repr,
            (self.requestline or "").rsplit(" ", 1)[0],
        )


def set_logger():
    level = logging.INFO
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    logger.addHandler(handler)


DISPLAY = """
 ┌─────────────────────────────────────────────────┐
 │   Clay is running                               │
 │                                                 │
 │   - Your machine:  {local}│
 │   - Your network:  {network}│
 │                                                 │
 │   Press `ctrl+c` to quit.                       │
 └─────────────────────────────────────────────────┘
"""


def display_running_message(host, port):  # pragma:no cover
    import socket

    local = "{:<29}".format(f"http://{host}:{port}")
    local_ip = socket.gethostbyname(socket.gethostname())
    network = "{:<29}".format(f"http://{local_ip}:{port}")

    print(DISPLAY.format(local=local, network=network))


def make_app(clay):
    app = WSGIApp(clay)
    app.wsgi = WhiteNoise(
        app.wsgi,
        root=clay.static_path,
        prefix="static/",
        index_file=True,
        autorefresh=True,
    )
    return app
