from pathlib import Path
import yaml


__all__ = ("load_config", )


def load_config(settings, user_settings=None, src_files=None):
    """
    Negotiate a group of settings from the global defaults, the user-provided
    values and config files. The keys in the `settings` argument are the only
    settings that are considered valid.

    The priority of the values is:

        user_settings > src_files > settings

    Arguments:

        settings (dict):
            All the valid settings with its default values.

        user_settings (dict):
            The settings provided by the user. These overwrite the others.
            Any key that is not in the `settings` dict is ignored.

        src_files (list of str/Path):
            List of YAML files (with extensions) from where to try to read the
            default values of the settings provided by the user.
            The first one found is the one read, the others are ignored.
            These have priority over the global defaults but are overwritten
            by the user_settings.
            Any key that is not in the `settings` dict is ignored.

    Examples:

        >>> load_config({"a": 1}, {"a": 2})
        {'a': 2}

        >>> load_config({"a": 1, "b": 2}, {"b": 3})
        {'a': 1, 'b': 3}

        >>> load_config({"a": 1}, {"b": 2})
        {'a': 1}

    """
    assert user_settings or src_files
    user_settings = user_settings or {}
    user_defaults = _load_user_defaults(src_files)
    config = {}

    for key, default in settings.items():
        value = user_settings.get(key)
        if value is not None:
            config[key] = value
            continue
        value = user_defaults.get(key)
        if value is not None:
            config[key] = value
            continue
        config[key] = default

    return config


def _load_user_defaults(src_files):
    for path in src_files or []:
        path = Path(path)
        if not path.exists():
            continue
        return yaml.safe_load(path.read_text()) or {}
    return {}
