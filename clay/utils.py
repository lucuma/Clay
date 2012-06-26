# -*- coding: utf-8 -*-
"""
# Clay.utils

"""
from datetime import datetime
import errno
import io
import math
import os
import re
import shutil
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        pass


def is_binary(filepath):
    """Return True if the given filename is binary.
    """
    CHUNKSIZE = 1024
    with io.open(filepath, 'rb') as f:
        while 1:
            chunk = f.read(CHUNKSIZE)
            if '\0' in chunk: # found null byte
                return True
            if len(chunk) < CHUNKSIZE:
                break
    return False


def walk_dir(path, callback, ignore=None):
    ignore = ignore or ()
    for folder, subs, files in os.walk(path):
        for filename in files:
            if filename.startswith(ignore):
                continue
            relpath = os.path.relpath(os.path.join(folder, filename), path)
            callback(relpath)


def make_dirs(*lpath):
    path = os.path.join(*lpath)
    try:
        os.makedirs(os.path.dirname(path))
    except (OSError), e:
        if e.errno != errno.EEXIST:
            raise
    return path


def get_source(filepath):
    source = ''
    with io.open(filepath, encoding='utf-8') as f:
        source = f.read()
    return source


def make_file(filepath, content):
    if not isinstance(content, unicode):
        content = unicode(content, 'utf-8')
    with io.open(filepath, 'w+t', encoding='utf-8') as f:
        f.write(content)


def remove_file(filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass


def absolute_to_relative(content, relpath, theme_prefix=''):
    # ## Normalize the relative-by-default URLs to absolute
    # ## Eg: "foo.html" => "/foo.html"
    # rx_rel_url = r' (src|href)=[\'"]([a-zA-Z0-9_]+[^\'"\:]+)[\'"]'
    # abs_url = r' \1="/\2"'
    # content = re.sub(rx_rel_url, abs_url, content)

    ## Relativize all absolute URLs
    ## Eg: "/en/bar.html" => "en/bar.html", and "/" => "index.html"
    depth = relpath.count(os.path.sep)
    repl = '../' * depth
    rel_url = r' \1="%s\2"' % repl

    if theme_prefix:
        theme_prefix = theme_prefix.strip('/').replace(r'/', r'\/') + r'\/+'
        rx_abs_url = r' (src|href)=[\'"]\/+(?:%s)?([^\'"]+)' % theme_prefix
    else:
        rx_abs_url = r' (src|href)=[\'"]\/+([^\'"]+)'
    content = re.sub(rx_abs_url, rel_url, content)

    rx_abs_url = r' (src|href)=(?P<fence>[\'"])\/(?P=fence)'
    rel_url = r' \1="%sindex.html"' % repl
    content = re.sub(rx_abs_url, rel_url, content)

    return content


def get_processed_regex(processed_files):
    rx_processed = [[
        re.compile(r' (src|href)=(?P<fence>[\'"])(.*)%s((\?.*)?(\#.*)?)?(?P=fence)' % old),
        r' \1="\3%s\4"' % new
    ] for old, new in processed_files]
    return rx_processed


def replace_processed_names(content, rx_processed):
    for rxold, rxnew in rx_processed:
        content = re.sub(rxold, rxnew, content)
    return content


def get_file_mdate(filepath):
    mtime = os.path.getmtime(filepath)
    mdate = datetime.utcfromtimestamp(mtime)
    mdate -=  datetime.utcnow() - datetime.now()
    return mdate


def copy_if_has_change(path_in, path_out):
    if os.path.exists(path_out):
        oldt = os.path.getmtime(path_out)
        newt = os.path.getmtime(path_in)
        if oldt == newt:
            return
    shutil.copy2(path_in, path_out)


def _is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    to_unicode(strings_only=True).
    """
    return isinstance(obj, (
        types.NoneType,
        int, long,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal)
    )


def to_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a unicode object representing 's'. Treats bytestrings using the
    `encoding` codec.

    If strings_only is True, don't convert (some) non-string-like objects.

    --------------------------------
    Copied almost unchanged from Django <https://www.djangoproject.com/>
    Copyright © 2005-2011 Django Software Foundation.
    Used under the modified BSD license.
    """
    # Handle the common case first, saves 30-40% in performance when s
    # is an instance of unicode.
    if isinstance(s, unicode):
        return s
    if strings_only and _is_protected_type(s):
        return s
    encoding = encoding or 'utf-8'
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = u' '.join([to_unicode(arg, encoding, strings_only,
                        errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        if not isinstance(s, Exception):
            raise UnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = u' '.join([to_unicode(arg, encoding, strings_only,
                errors) for arg in s])
    return s


def filter_to_json(source_dict):
    return json.dumps(source_dict)

