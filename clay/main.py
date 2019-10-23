from pathlib import Path
import logging

import yaml


class Clay(object):
    def __init__(self, source_path, build_folder="build"):
        self.source_path = Path(source_path).resolve()
        self.build_path = source_path / self.build_folder
        self.config = self._load_config()
        self.filter_file = self._make_file_filter()

    def _load_config(self):
        config_path = self.source_path / "clay.yaml"
        if not config_path.exists():
            config_path = self.source_path / "clay.yml"
            if not config_path.exists():
                return {}
        try:
            return yaml.safe_load(config_path.read_text())
        except yaml.YAMLError:
            logging.error("INVALID CONFIG FILE")
            return

    def _make_file_filter(self):
        exclude = self.config("exclude")
        if not exclude:
            # Do not filter anything
            return lambda filepath: False
        include = self.config("include")
