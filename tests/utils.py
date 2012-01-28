# -*- coding: utf-8 -*-
import io
import os

from clay import Clay


HTTP_OK = 200
HTTP_NOT_FOUND = 404

proto = Clay(__file__)
c = proto.test_client()


def get_views_filepath(filename):
    return os.path.join(proto.source_dir, filename)


def get_build_filepath(filename):
    return os.path.join(proto.build_dir, filename)


def make_file(filepath, content):
    if not isinstance(content, unicode):
        content = unicode(content, 'utf-8')
    with io.open(filepath, 'w+t') as f:
        f.write(content)
    return filepath


def make_view(filename, content):
    filepath = get_views_filepath(filename)
    make_file(filepath, content)
    return filepath


def read_file(filepath):
    with io.open(filepath) as f:
        content = f.read()
    content = content.encode('utf8')
    return content


def remove_file(filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass

