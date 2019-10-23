from pathlib import Path
import logging

import hecto
import yaml

from .utils import load_config
from .utils import make_path_matcher
from .utils import make_path_filter
from .utils import make_path_filter


GLOBAL_DEFAULTS = {
    "exclude": [],
    "include": [],
}


class Clay(object):
    def __init__(self, source_path, exclude=None, include=None):
        self.source_path = Path(source_path).resolve()
        self.config = self._load_config({"exclude": exclude, "include": include})

    def build(self, build_folder="build", quiet=False):
        dst_path = self.source_path / build_folder
        exclude = self.config["exclude"] + [
            "clay.yaml",
            "clay.yml",
            build_folder,
            f"{build_folder}/*",
        ]

        hecto.copy(
            self.source_path,
            dst_path,
            render=["!static/*"],
            exclude=exclude,
            include=self.config["include"],
            envops={
                "block_start_string": "{%",
                "block_end_string": "%}",
                "variable_start_string": "{{",
                "variable_end_string": "}}",
            },
            quiet=quiet
        )

    def _load_config(self, options):
        try:
            return load_config(
                GLOBAL_DEFAULTS,
                options,
                [self.source_path / "clay.yaml", self.source_path / "clay.yml"],
            )
        except yaml.YAMLError:
            logging.error("Invalid config file `clay.yaml`.")
            return GLOBAL_DEFAULTS
