# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from os.path import dirname

from flask import request


def _norm_url(url):
    url = url.rstrip('/')
    if url.startswith('/'):
        return url
    baseurl = dirname(request.path.strip('/'))
    if baseurl:
        return '/' + '/'.join([baseurl, url])
    return '/' + url


def active(*url_patterns, **kwargs):
    partial = kwargs.get('partial')

    path = request.path.rstrip('/')
    resp = u''
    # for backward compatibility
    if len(url_patterns) == 1 and isinstance(url_patterns[0], (list, tuple)):
        url_patterns = url_patterns[0]
    #
    for url in url_patterns:
        url = _norm_url(url)
        if fnmatch(path, url) or (partial and path.startswith(url)):
            return 'active'
    return resp
