import re


__all__ = ("get_relative_url", "make_absolute_urls_relative")

RX_ABS_URL = re.compile(
    r"""\s(src|href|data-[a-z0-9_-]+)\s*=\s*['"](\/(?:[a-z0-9_-][^'"]*)?)[\'"]""",
    re.UNICODE | re.IGNORECASE,
)


def get_relative_url(base_path, relpath, currurl):
    depth = relpath.count("/")
    url = (r"../" * depth) + currurl.lstrip("/")

    if not url:
        return "index.html"
    if (base_path / relpath).is_dir() or url.endswith("/"):
        return url.rstrip("/") + "/index.html"

    return url


def make_absolute_urls_relative(base_path, relpath, content):
    relpath = str(relpath)

    for attr, url in RX_ABS_URL.findall(content):
        newurl = get_relative_url(base_path, relpath, url)
        repl = r' %s="%s"' % (attr, newurl)
        content = re.sub(RX_ABS_URL, repl, content, count=1)

    return content
