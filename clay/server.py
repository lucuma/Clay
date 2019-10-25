from datetime import datetime
from gevent import pywsgi
from whitenoise import WhiteNoise

import logging
import sys


logger = logging.getLogger()


class WSGIApp(object):
    def __init__(self, clay):
        self.clay = clay

    def call(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response):
        status = "200 OK"
        data = b"Hello, World!\n"
        response_headers = [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(data))),
        ]
        start_response(status, response_headers)
        return [data]

    def run(self, host, port):
        set_logger()
        server = pywsgi.WSGIServer(
            (host, port),
            self.wsgi,
            handler_class=ClayHandler
        )
        display_running_message(host, port)
        try:
            return server.serve_forever()
        except KeyboardInterrupt:
            print("\n Goodbye!\n")


STATUS_REPR = {
    "200": "✔︎",
    "404": "𐄂",
}


class ClayHandler(pywsgi.WSGIHandler):
    def format_request(self):
        now = datetime.now()
        if isinstance(self.client_address, tuple):
            client_address = self.client_address[0]
        else:
            client_address = self.client_address
        status = self._orig_status.split()[0]
        status_repr = STATUS_REPR.get(status, status)

        return " {} {} -> {} {}".format(
            now.strftime("%H:%M:%S"),
            client_address or "?",
            (self.requestline or "").rsplit(" ", 1)[0],
            status_repr,
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
