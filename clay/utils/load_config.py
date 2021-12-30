from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


__all__ = ("load_config",)


def load_config(
    settings: Dict[str, Any],
    src_files: Optional[List[Union[str, Path]]] = None
):
    """
    Negotiate a group of settings from the global defaults
    and config files.
    The keys in the `settings` argument are the only settings that
    are considered valid.

    Arguments:

    - settings (dict):
        All the valid settings with its default values.

    - src_files (list of str/Path):
        List of YAML files (with extensions) from where to try to read the
        default values of the settings provided by the user.
        The first one found is the one read, the others are ignored.
        These have priority over the global defaults but are overwritten
        by the user_settings.
        Any key that is not in the `settings` dict is ignored.

    """
    defaults = _load_defaults(src_files)
    config = {}

    for key, default in settings.items():
        value = defaults.get(key)
        if value is not None:
            config[key] = value
            continue
        config[key] = default

    return config


def _load_defaults(src_files):
    for path in src_files or []:
        path = Path(path)
        if not path.exists():
            continue
        return yaml.safe_load(path.read_text()) or {}
    return {}
