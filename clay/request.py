import re

import multipart

from .utils import MultiDict


RX_INDEX = re.compile(r"/index\.html$")


class Request:
    def __init__(self, environ=None, path=None):
        environ = environ or {}
        self.environ = environ
        self.path = path or self.get_path()
        self.query = self.get_query()
        self.ajax = self.is_xhr
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.remote_addr = environ.get("REMOTE_ADDR", "127.0.0.1")

    @property
    def is_xhr(self):
        if "HTTP_X_REQUESTED_WITH" in self.environ:
            return self.environ["HTTP_X_REQUESTED_WITH"] == "XMLHttpRequest"
        return False

    @property
    def parent_path(self):
        return re.sub(RX_INDEX, "", self.path)

    def get_path(self):
        path_info = self.environ.get("PATH_INFO")
        if not path_info:
            return ""
        path = path_info.encode("iso-8859-1", "replace").decode("utf-8", "replace")
        return path[1:] + "index.html" if path.endswith("/") else path[1:]

    def get_query(self):
        query_string = self.environ.get("QUERY_STRING")
        return parse_query_string(query_string)


def parse_query_string(query_string):
    """Parse a query string into a MultiDict.

    Query string parameters are assumed to use standard form-encoding.

    Arguments are:

        query_string (str):
            The value of the HTTP_QUERY_STRING header.

    Returns (MultiDict):

        A MultiDict of `name: [value1, value2, ...]` pairs.
        Like with all MultiDict, the *values* are always a list, even when
        only one is found for that key.

    """
    query = MultiDict()
    if not query_string:
        return query

    data = multipart.parse_qs(query_string, keep_blank_values=True)
    for key, values in data.items():
        query[key] = [True if value == "" else value for value in values]
    return query
