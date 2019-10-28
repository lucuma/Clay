import pkg_resources


try:
    __version__ = pkg_resources.require("clay")[0].version
except Exception:  # pragma: no cover
    __version__ = None
