import mimetypes
import socket
from urllib.parse import quote

import gunicorn.app.base
from whitenoise import WhiteNoise

from .request import Request
from .utils import make_active_helper


def _get_local_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if not ip.startswith("127."):
        return ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        sock.connect(("8.8.8.8", 1))
        ip = sock.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        sock.close()
    return ip


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


def _display_running_message(host, port):  # pragma: no cover
    local = "{:<29}".format(f"http://{host}:{port}")
    network = "{:<29}".format(f"http://{_get_local_ip()}:{port}")

    print(DISPLAY.format(local=local, network=network))


def on_starting(server):
    """Gunicorn hook"""
    _display_running_message(*server.address[0])


class GunicornMiddleware(gunicorn.app.base.BaseApplication):

    def __init__(self, app, **options):
        self.app = app
        self.options = options
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.app


class WSGIApp:
    def __init__(self, clay):
        self.clay = clay

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response):
        request = Request(environ)
        body, status, headers = self.call(request)
        if hasattr(body, "encode"):
            body = body.encode("utf8")

        headers.append(("Content-Length", str(len(body))))
        start_response(status, headers)
        return [body]

    def call(self, request):
        path = request.path
        print(path)
        if not self.clay.file_exists(path):
            print("file doesnt exists", path)
            path += "/index.html"
            if not self.clay.file_exists(path):
                return self.not_found(request)

        active = make_active_helper(request)
        if request.method == "HEAD":
            body = ""
        else:
            print("rendering file", path)
            body = self.clay.render_file(path, request=request, active=active)
        mime = mimetypes.guess_type(path)[0] or "text/plain"
        response_headers = [("Content-Type", mime)]
        return body, "200 OK", response_headers

    def not_found(self, request):
        mime = "text/plain"
        body = f"File {request.path} not found."
        active = make_active_helper(request)

        for path in ["not-found.html", "_notfound.html", "404.html"]:
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

    def run(self, host, port):  # pragma: no cover
        server = GunicornMiddleware(
            self,
            bind=f"{host}:{port}",
            worker_class="eventlet",
            accesslog="-",
            access_log_format="%(h)s %(m)s %(U)s -> HTTP %(s)s",
            on_starting=on_starting
        )
        server.run()


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
