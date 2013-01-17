# -*- coding: utf-8 -*-
from flask import request


def to_unicode(s, encoding='utf8', errors='strict'):
    return s.decode(encoding, errors)


def _norm_url(url):
    return '/' + url.strip('/')


def active(url='/', partial=False):
    path = request.path.rstrip('/')
    resp = u''
    patterns = url if isinstance(url, (list, tuple)) else [url]

    for url in patterns:
        url = _norm_url(url)
        if path == url or (partial and path.startswith(url)):
            return 'active'

    return resp

