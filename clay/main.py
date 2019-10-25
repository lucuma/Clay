from pathlib import Path
import glob
import logging
import random
import os

import hecto
import yaml

from .utils import load_config
from .utils import make_absolute_urls_relative


GLOBAL_DEFAULTS = {
    "exclude": [],
    "include": [],
}

MESSAGES = [
    "Post processing",
    "Relativizing URLs",
    "Distilling enjoyment",
    "Adding emotional depth",
    "Filtering the ozone",
    "Testing for perfection",
    "Stretching the truth",
    "Optimizing for happiness",
    "Swapping time and space",
    "Reversing the polarity",
    "Self affirming",
    "Extracting meaning",
]


class Clay(object):
    def __init__(self, source_path, exclude=None, include=None):
        self.source_path = Path(source_path).resolve()
        self.config = self._load_config({"exclude": exclude, "include": include})

    @property
    def static_path(self):
        return self.source_path / "static"

    def build(self, build_folder="build", quiet=False):
        dst_path = self.source_path / build_folder
        exclude = self.config["exclude"] + [
            "clay.yaml",
            "clay.yml",
            build_folder,
            f"{build_folder}/*",
        ]

        def render_as(src_path, dst_path):
            if str(dst_path).startswith("static/"):
                return None
            return dst_path

        hecto.copy(
            self.source_path,
            dst_path,
            exclude=exclude,
            include=self.config["include"],
            envops={
                "block_start_string": "{%",
                "block_end_string": "%}",
                "variable_start_string": "{{",
                "variable_end_string": "}}",
            },
            render_as=render_as,
            force=True,
            quiet=quiet
        )
        if not quiet:
            print()
        self._post_process(dst_path, quiet=quiet)

    def random_messages(self, num=2):
        return random.sample(MESSAGES, num)

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

    def _print_random_messages(self, num=2, quiet=False):
        if not quiet:
            for message in self.random_messages(num):
                print(f" {message}...")

    def _post_process(self, dst_path, quiet=False):
        self._print_random_messages(num=2, quiet=quiet)
        self._relativize_urls(dst_path)
        self._print_random_messages(num=1, quiet=quiet)

    def _relativize_urls(self, dst_path):
        html_files = glob.glob(f"{dst_path}/**/*.html", recursive=True)
        for html_file in html_files:
            relpath = os.path.relpath(html_file, dst_path)
            html_file = Path(html_file)
            content = html_file.read_text()
            new_content = make_absolute_urls_relative(dst_path, relpath, content)
            html_file.write_text(new_content)
