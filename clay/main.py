import os
import random
from datetime import datetime, timezone
from pathlib import Path

import jinja2
import yaml

from .utils.binaries import KNOWN_BINARIES
from .utils.blueprint_render import BlueprintRender
from .utils.jinja_includewith import IncludeWith
from .utils.load_config import load_config
from .utils.make_matcher import make_filter, make_matcher


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

BUILD_FOLDER = "build"
STATIC_FOLDER = "static"


def utcnow():
    return datetime.now(tz=timezone.utc)


@jinja2.pass_context
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
}
JINJA_FILTERS = {"shuffle": shuffle}

BLUEPRINT = Path(__file__).resolve().parent / "blueprint"
DEFAULT_CONFIG = {
    "exclude": (
        ".*",
        ".*/*",
        "~*",
        "~*/*",
        "_*",
        "_*/*",
        "node_modules",
        "node_modules/*",
        "package.json",
        "package-lock.json",
    ),
    "include": ("favicon.ico"),
    "jinja_extensions": (IncludeWith,),
    "binaries": [],
}
EXCLUDE_PAGE_PATTERNS = (
    "clay.yaml",
    "clay.yml",
    STATIC_FOLDER,
    BUILD_FOLDER,
    f"{STATIC_FOLDER}/*",
    f"{BUILD_FOLDER}/*",
)


class Clay:
    def __init__(self, source_path):
        self.source_path = Path(source_path).resolve()
        self.build_path = self.source_path / BUILD_FOLDER
        self.static_path = self.source_path / STATIC_FOLDER
        self.config = config = self.load_config()
        print(self.config)

        must_exclude = make_matcher(config["exclude"])
        must_include = make_matcher(config["include"])
        self.must_filter = make_filter(must_exclude, must_include)
        self.is_binary = make_matcher(config["binaries"])

        globals_ = JINJA_GLOBALS.copy()
        globals_.update(
            {
                "list_pages": self.list_pages,
            }
        )
        self.render = BlueprintRender(
            src=self.source_path,
            dst=self.build_path,
            must_filter=self.must_filter,
            is_binary=self.is_binary,
            static_folder=STATIC_FOLDER,
            globals_=globals_,
            filters_=JINJA_FILTERS,
            extensions=config["jinja_extensions"],
        )
        self.exclude_page = make_matcher(self.config["exclude"] + EXCLUDE_PAGE_PATTERNS)

    def file_exists(self, path):
        if self.must_filter(path):
            return False
        return (self.source_path / path).is_file()

    def render_file(self, path, **data):
        return self.render.render_content(path, **data)

    def build(self, **data):
        self.render(**data)
        self.print_random_messages(num=3)

    def list_pages(self, folder=".", sub=True):
        """List all the available pages outside the static and build folders.

        If `folder` is not None, it list only the pages inside that folder.
        Use `folder="."` to show the pages of the root folder but not those in subfolders
        """
        source_path = self.source_path / folder.replace("..", "")

        pages = []
        for root, _, files in os.walk(source_path):
            relpath = str(Path(root).relative_to(source_path))
            if relpath == ".":
                relpath = ""

            if relpath and not sub:
                break

            if self.exclude_page(relpath):
                continue

            for file in sorted(files):
                page = os.path.join(relpath, file)
                if self.exclude_page(page):
                    continue
                pages.append(page)

        return pages

    def load_config(self):
        try:
            config = load_config(
                DEFAULT_CONFIG,
                [self.source_path / "clay.yaml", self.source_path / "clay.yml"],
            )
        except yaml.YAMLError:
            print("ERROR: Invalid config file `clay.yaml`.")
            return DEFAULT_CONFIG

        config["binaries"] = tuple(set(config["binaries"] + KNOWN_BINARIES))

        for key in "exclude,include,jinja_extensions".split(","):
            config[key] = tuple(config[key])
        return config

    def print_random_messages(self, num=2):
        for message in random.sample(MESSAGES, num):
            print(f" {message}...")
