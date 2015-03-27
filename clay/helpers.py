# coding=utf-8
from datetime import datetime
import errno
from fnmatch import fnmatch
import io
import os
import shutil
import unicodedata


def to_unicode(txt, encoding='utf8'):
    if not isinstance(txt, basestring):
        txt = str(txt)
    if isinstance(txt, unicode):
        return txt
    return unicode(txt, encoding)


def unormalize(text, form='NFD'):
    return unicodedata.normalize(form, text)


def fullmatch(path, pattern):
    path = unormalize(path)
    name = os.path.basename(path)
    return fnmatch(name, pattern) or fnmatch(path, pattern)


def make_dirs(*lpath):
    path = os.path.join(*lpath)
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return path


def create_file(path, content, encoding='utf8'):
    if not isinstance(content, unicode):
        content = unicode(content, encoding)
    make_dirs(os.path.dirname(path))
    with io.open(path, 'w+t', encoding=encoding) as f:
        f.write(content)


def copy_if_updated(path_in, path_out):
    if os.path.exists(path_out):
        newt = os.path.getmtime(path_in)
        currt = os.path.getmtime(path_out)
        if currt >= newt:
            return
    shutil.copy2(path_in, path_out)


def get_updated_datetime(path):
    ut = os.path.getmtime(path)
    return datetime.fromtimestamp(ut)


def sort_paths_dirs_last(paths):
    def dirs_last(a, b):
        return cmp(a[0].count('/'), b[0].count('/')) or cmp(a[0], b[0])

    return sorted(paths, cmp=dirs_last)
