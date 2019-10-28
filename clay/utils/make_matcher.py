from fnmatch import fnmatch
from functools import reduce
import os
import unicodedata

__all__ = ("make_matcher", "make_filter", )


def _normalize_str(text, form="NFD"):
    """Normalize unicode text. Uses the NFD algorithm by default."""
    return unicodedata.normalize(form, text)


def _fullmatch(path, pattern):
    path = _normalize_str(str(path))
    name = os.path.basename(path)
    return fnmatch(name, pattern) or fnmatch(path, pattern)


def _match(path, patterns):
    return reduce(
        lambda r, pattern: r or _fullmatch(path, pattern),
        patterns,
        False)


def make_matcher(patterns):
    """Returns a function that evaluates if a file or folder name must be
    filtered out, and another that evaluates if a file must be skipped.
    The compared paths are first converted to unicode and decomposed.
    This is neccesary because the way PY2.* `os.walk` read unicode
    paths in different filesystems. For instance, in OSX, it returns a
    decomposed unicode string. In those systems, u'ñ' is read as `\u0303`
    instead of `\xf1`.
    """
    patterns = [_normalize_str(pattern) for pattern in patterns]

    def path_match(path):
        return _match(path, patterns)

    return path_match


def make_filter(must_exclude, must_include):

    def must_filter(path):
        return must_exclude(path) and not must_include(path)

    return must_filter
