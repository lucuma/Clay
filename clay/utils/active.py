from fnmatch import fnmatch
import re


__all__ = ("make_active_helper", )


def make_active_helper(request):
    def active(*url_patterns, partial=False, class_name="active"):
        curr_path = re.sub("index.html$", "", request.path).strip("/")
        for urlp in url_patterns:
            urlp = re.sub("index.html$", "", urlp.strip("/")).strip("/")
            if fnmatch(curr_path, urlp) or (partial and curr_path.startswith(urlp)):
                return class_name
        return ""

    return active
