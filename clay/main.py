import glob
import logging
import os
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

import hecto
import yaml

from .request import Request
from .utils import (
    IncludeWith,
    JinjaRender,
    load_config,
    make_absolute_urls_relative,
    make_active_helper,
    make_filter,
    make_matcher,
)

BLUEPRINT = Path(__file__).resolve().parent / "blueprint"

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
    "Self-affirming",
    "Extracting meaning",
]


def utcnow():
    return datetime.now(tz=timezone.utc)


def thumbnail(path, *args, **kwargs):
    """For backwards compatibility."""
    return "/" + path.lstrip("/")


JINJA_GLOBALS = {
    "now": utcnow,
    "dir": dir,
    "enumerate": enumerate,
    "map": map,
    "zip": zip,
    "len": len,
    # backwards compatibility
    "thumbnail": thumbnail,
}

JINJA_EXTENSIONS = ("jinja2.ext.with_", IncludeWith)


class Clay(object):
    def __init__(self, source_path, exclude=None, include=None):
        source_path = Path(source_path).resolve()
        if self.is_classic_style(source_path):
            self.classic_style = True
            source_path = source_path / "source"
            self.create_yaml_if_dont_exists(source_path)
        else:
            self.classic_style = False

        self.source_path = source_path
        self.config = self._load_config({
            "exclude": exclude,
            "include": include,
        })
        extensions = tuple(self.config["jinja_extensions"])
        self.jinja_extensions = JINJA_EXTENSIONS + extensions
        self.render = JinjaRender(
            self.source_path,
            data=JINJA_GLOBALS.copy(),
            extensions=self.jinja_extensions
        )

        must_exclude = make_matcher(self.config["exclude"])
        must_include = make_matcher(self.config["include"])
        self.must_filter = make_filter(must_exclude, must_include)

    @property
    def static_path(self):
        return self.source_path / "static"

    def is_classic_style(self, source_path):
        return (
            (source_path / "source").is_dir()
            and not (source_path / "index").exists()
        )

    def create_yaml_if_dont_exists(self, source_path):
        path = source_path / "clay.yaml"
        if not path.exists():
            shutil.copy2(str(BLUEPRINT / "clay.yaml"), str(path))

    def file_exists(self, path):
        if self.must_filter(path):
            return False
        return (self.source_path / path).is_file()

    def render_file(self, path, **data):
        return self.render(path, **data)

    def build(self, build_folder="build", quiet=False):
        if self.classic_style:
            dst_path = self.source_path / ".." / build_folder
        else:
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
            data=JINJA_GLOBALS.copy(),
            exclude=exclude,
            include=self.config["include"],
            envops={
                "block_start_string": "{%",
                "block_end_string": "%}",
                "variable_start_string": "{{",
                "variable_end_string": "}}",
                'extensions': self.jinja_extensions,
            },
            render_as=render_as,
            get_context=get_context,
            force=True,
            quiet=quiet,
        )
        if not quiet:
            print()
        self._post_process(dst_path, quiet=quiet)

    def random_messages(self, num=3):
        return random.sample(MESSAGES, num)

    def _load_config(self, options):
        defaults = {
            "exclude": [".*", ".*/**/*"],
            "include": [],
            "jinja_extensions": [],
        }
        try:
            return load_config(
                defaults,
                options,
                [self.source_path / "clay.yaml", self.source_path / "clay.yml"],
            )
        except yaml.YAMLError:
            logging.error("Invalid config file `clay.yaml`.")
            return defaults

    def _post_process(self, dst_path, quiet=False):
        self._print_random_messages(num=3, quiet=quiet)
        self._relativize_urls(dst_path)

    def _print_random_messages(self, num=2, quiet=False):
        if not quiet:
            for message in self.random_messages(num):
                print(f" {message}...")

    def _relativize_urls(self, dst_path):
        html_files = glob.glob(f"{dst_path}/**/*.html", recursive=True)
        for html_file in html_files:
            relpath = os.path.relpath(html_file, dst_path)
            html_file = Path(html_file)
            content = html_file.read_text()
            new_content = make_absolute_urls_relative(dst_path, relpath, content)
            html_file.write_text(new_content)


def render_as(src_path, dst_path):
    if str(dst_path).startswith("static/"):
        return None
    return dst_path


def get_context(path):
    request = Request()
    request.path = str(path).replace("\\", "/").strip("/")
    active = make_active_helper(request)
    return {"request": request, "active": active}
