# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from os.path import dirname
import re

from flask import request


def norm_url(url):
    url = url.strip().rstrip('/')
    url = re.sub('index.html$', '', url).rstrip('/')
    if url.startswith('/'):
        return url
    baseurl = dirname(request.path.strip('/'))
    if baseurl:
        return '/' + '/'.join([baseurl, url])
    return '/' + url


def active(*url_patterns, **kwargs):
    partial = kwargs.get('partial')

    path = norm_url(request.path)

    # Accept single patterns also
    if len(url_patterns) == 1 and isinstance(url_patterns[0], (list, tuple)):
        url_patterns = url_patterns[0]

    for urlp in url_patterns:
        urlp = norm_url(urlp)
        if fnmatch(path, urlp) or (partial and path.startswith(urlp)):
            return 'active'
    return u''
