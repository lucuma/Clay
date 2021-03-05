import glob
import logging
import os
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

import hecto
import jinja2
import yaml
from hecto.utils import make_matcher

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


@jinja2.contextfilter
def shuffle(context, value):
    iter = value[:]
    random.shuffle(iter)
    return iter


JINJA_GLOBALS = {
    "now": utcnow,
    "dir": dir,
    "enumerate": enumerate,
    "map": map,
    "zip": zip,
    "len": len,
    "datetime": datetime,
    # backwards compatibility
    "thumbnail": thumbnail,
}
JINJA_FILTERS = {"shuffle": shuffle}
JINJA_EXTENSIONS = ("jinja2.ext.with_", IncludeWith)

STATIC_FOLDER = "static"
BUILD_FOLDER = "build"


class Clay:
    def __init__(self, source_path, exclude=None, include=None):
        source_path = Path(source_path).resolve()
        if self._is_classic_style(source_path):
            self.classic_style = True
            source_path = source_path / "source"
            self._create_yaml_if_dont_exists(source_path)
        else:
            self.classic_style = False

        self.source_path = source_path
        self.config = self._load_config(
            {
                "exclude": exclude,
                "include": include,
            }
        )
        extensions = tuple(self.config["jinja_extensions"])
        self.jinja_extensions = JINJA_EXTENSIONS + extensions
        self.render = JinjaRender(
            self.source_path,
            data=self.jinja_globals,
            filters_=JINJA_FILTERS,
            extensions=self.jinja_extensions,
        )

        must_exclude = make_matcher(self.config["exclude"])
        must_include = make_matcher(self.config["include"])
        self.must_filter = make_filter(must_exclude, must_include)
        self.is_binary = make_matcher(self.config["binaries"])

    @property
    def jinja_globals(self):
        jg = JINJA_GLOBALS.copy()
        jg.update({"list_pages": self.list_pages})
        return jg

    @property
    def static_path(self):
        return self.source_path / STATIC_FOLDER

    @property
    def build_path(self):
        if self.classic_style:
            return self.source_path / ".." / BUILD_FOLDER
        return self.source_path / BUILD_FOLDER

    @property
    def exclude_patterns(self):
        return self.config["exclude"] + [
            "clay.yaml",
            "clay.yml",
            BUILD_FOLDER,
            f"{BUILD_FOLDER}/*",
        ]

    def file_exists(self, path):
        if self.must_filter(path):
            return False
        return (self.source_path / path).is_file()

    def render_file(self, path, **data):
        if self.is_binary(path):
            return (self.source_path / path).read_bytes()
        return self.render(path, **data)

    def build(self, quiet=False):
        hecto.copy(
            self.source_path,
            self.build_path,
            data=self.jinja_globals,
            exclude=self.exclude_patterns,
            include=self.config["include"],
            envops={
                "block_start_string": "{%",
                "block_end_string": "%}",
                "variable_start_string": "{{",
                "variable_end_string": "}}",
                "extensions": self.jinja_extensions,
            },
            jinja_filters=JINJA_FILTERS,
            render_as=self._render_as,
            get_context=self._get_context,
            force=True,
            quiet=quiet,
        )
        if not quiet:
            print()
        self._post_process(self.build_path, quiet=quiet)

    def list_pages(self, folder=".", sub=True):
        """List all the available pages outside the static and build folders.

        If `folder` is not None, it list only the pages inside that folder.
        Use `folder="."` to show the pages of the root folder but not those in subfolders
        """
        exclude = make_matcher(
            self.exclude_patterns + [STATIC_FOLDER, f"{STATIC_FOLDER}/*"]
        )
        source_path = self.source_path / folder.replace("..", "")

        pages = []
        for root, _, files in os.walk(source_path):
            relpath = str(Path(root).relative_to(source_path))
            if relpath == ".":
                relpath = ""

            if relpath and not sub:
                break

            if exclude(relpath):
                continue

            for file in sorted(files):
                page = os.path.join(relpath, file)
                if exclude(page):
                    continue
                pages.append(page)

        return pages

    # Private

    def _is_classic_style(self, source_path):
        return (source_path / "source").is_dir() and not (
            source_path / "index"
        ).exists()

    def _create_yaml_if_dont_exists(self, source_path):
        path = source_path / "clay.yaml"
        if not path.exists():
            shutil.copy2(str(BLUEPRINT / "clay.yaml"), str(path))

    def _load_config(self, options):
        defaults = {
            "exclude": [
                ".*",
            ],
            "include": [],
            "jinja_extensions": [],
            "binaries": [],
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
            for message in self._random_messages(num):
                print(f" {message}...")

    def _random_messages(self, num=3):
        return random.sample(MESSAGES, num)

    def _relativize_urls(self, dst_path):
        html_files = glob.glob(f"{dst_path}/**/*.html", recursive=True)
        for html_file in html_files:
            relpath = os.path.relpath(html_file, dst_path)
            html_file = Path(html_file)
            content = html_file.read_text()
            new_content = make_absolute_urls_relative(dst_path, relpath, content)
            html_file.write_text(new_content)

    def _render_as(self, src_path, dst_path):
        dst = str(dst_path)
        if dst.startswith("static/") or self.is_binary(dst):
            return None
        return dst_path

    def _get_context(self, path):
        request = Request()
        request.path = str(path).replace("\\", "/").strip("/")
        active = make_active_helper(request)
        return {"request": request, "active": active}
