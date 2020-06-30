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
    """Returns a function that evaluates if a path match one of the patterns.

    The compared paths are first converted to unicode and decomposed.
    This is neccesary because the way `os.walk` read unicode paths could vary.
    For instance, it might returns a decomposed unicode string reading
    the character "ñ" as `\u0303` instead of `\xf1`.
    """
    patterns = [_normalize_str(pattern) for pattern in patterns]

    def path_match(path):
        return _match(path, patterns)

    return path_match


def make_filter(must_exclude, must_include):
    """Returns a function that evaluates if a path name must be
    excluded or not.
    """

    def must_filter(path):
        return must_exclude(path) and not must_include(path)

    return must_filter
