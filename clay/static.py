
import os
from zlib import adler32

from cherrypy.lib import httputil, file_generator_limited
from werkzeug.http import quote_etag
from werkzeug.exceptions import RequestedRangeNotSatisfiable
import mimetypes
mimetypes.init()

NEW_MIMETYPES = {
    '.dwg': 'image/x-dwg',
    '.ico': 'image/x-icon',
    '.bz2': 'application/x-bzip2',
    '.gz': 'application/x-gzip',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
    '.potx': 'application/vnd.openxmlformats-officedocument.presentationml.template',
    '.ppsx': 'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.sldx': 'application/vnd.openxmlformats-officedocument.presentationml.slide',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
    '.xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
    '.xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
}
for name, value in NEW_MIMETYPES.items():
    mimetypes.types_map[name] = value


def serve_file(path):
    headers = {}

    st = os.stat(path)

    etag = 'clay-{0}-{1}-{2}'.format(
        os.path.getmtime(path),
        os.path.getsize(path),
        adler32(path.encode('utf-8')) & 0xffffffff
    )
    headers['ETag'] = quote_etag(etag)

    # Set the Last-Modified response header, so that
    # modified-since validation code can work.
    headers['Last-Modified'] = httputil.HTTPDate(st.st_mtime)

    _, ext = os.path.splitext(path)
    content_type = mimetypes.types_map.get(ext, None)
    headers['Content-Type'] = content_type or 'text/plain'

    fileobj = open(path, 'rb')
    return serve_fileobj(fileobj, headers, st.st_size)


def serve_fileobj(fileobj, headers, content_length):
    status_code = 200
    headers["Accept-Ranges"] = "bytes"

    r = httputil.get_ranges(headers.get('Range'), content_length)

    if r == []:
        headers['Content-Range'] = "bytes */{0}".format(content_length)
        message = "Invalid Range (first-byte-pos greater than Content-Length)"
        raise RequestedRangeNotSatisfiable(message)

    if not r:
        headers['Content-Length'] = content_length
        return fileobj, headers, status_code

    # Return a multipart/byteranges response.
    status_code = 206

    if len(r) == 1:
        # Return a single-part response.
        start, stop = r[0]
        if stop > content_length:
            stop = content_length
        r_len = stop - start

        headers['Content-Range'] = "bytes {0}-{1}/{2}".format(
            start, stop - 1, content_length
        )
        headers['Content-Length'] = r_len
        fileobj.seek(start)
        body = file_generator_limited(fileobj, r_len)
        return body, headers, status_code

    try:
        # Python 3
        from email.generator import _make_boundary as make_boundary
    except ImportError:
        # Python 2
        from mimetools import choose_boundary as make_boundary

    boundary = make_boundary()
    content_type = "multipart/byteranges; boundary={0}".format(boundary)
    headers['Content-Type'] = content_type
    if "Content-Length" in headers:
        del headers["Content-Length"]

    def file_ranges():
        for start, stop in r:
            yield "--" + boundary
            yield "\r\nContent-type: {0}".format(content_type)
            yield "\r\nContent-range: bytes {0}-{1}/{2}\r\n\r\n".format(
                    start, stop - 1, content_length
                  )
            fileobj.seek(start)

            gen = file_generator_limited(fileobj, stop - start)
            for chunk in gen:
                yield chunk
            yield "\r\n"

        yield "--" + boundary + "--"

    body = file_ranges()
    return body, headers, status_code
