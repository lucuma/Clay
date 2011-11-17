"""
# Clay.utils

"""
import errno
import io
import os
import re


def walk_dir(path, callback, ignore='.'):
    for folder, subs, files in os.walk(path):
        ffolder = os.path.relpath(folder, path)
        for filename in files:
            if filename.startswith(ignore):
                continue
            relpath = os.path.join(ffolder, filename) \
                .lstrip('.').lstrip('/')
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
    with io.open(filepath) as f:
        source = f.read()
    return source


def make_file(filepath, content):
    if not isinstance(content, unicode):
        content = unicode(content, 'utf-8')
    with io.open(filepath, 'w+t') as f:
        f.write(content)


def get_processed_regex(processed_files):
    rx_processed = [[
        re.compile(r' (src|href)=[\'"]%s[\'"]' % old),
        r' \1="%s"' % new
    ] for old, new in processed_files]
    return rx_processed


def replace_processed_names(content, rx_processed):
    for rxold, rxnew in rx_processed:
        content = re.sub(rxold, rxnew, content)
    return content

