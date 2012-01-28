# -*- coding: utf-8 -*-
"""
    # Clay.render
"""
import os

from jinja2 import PackageLoader, ChoiceLoader, FileSystemLoader
from shake import Render as JinjaRender
from shake import TemplateNotFound

from . import utils
from .config import *

## Processors
## This method is longer but clearer than using `import_module`
enabled_processors = {}

from .processors import scss_
if scss_.enabled:
    for ext in scss_.extensions_in:
        enabled_processors[ext] = scss_

from .processors import less_
if less_.enabled:
    for ext in less_.extensions_in:
        enabled_processors[ext] = less_

from .processors import clevercss_
if clevercss_.enabled:
    for ext in clevercss_.extensions_in:
        enabled_processors[ext] = clevercss_

from .processors import coffeescript_
if coffeescript_.enabled:
    for ext in coffeescript_.extensions_in:
        enabled_processors[ext] = coffeescript_


text_files = ['.html', '.htm', '.txt', '.csv',]


class Render(object):

    def __init__(self, source_dir, settings):
        self.source_dir = source_dir
        self.settings = settings
        loader = ChoiceLoader([
            FileSystemLoader(source_dir),
            PackageLoader('clay', 'src'),
        ])
        self.render = JinjaRender(loader=loader)
    
    def __call__(self, path, **env):
        fn, ext = os.path.splitext(path)
        processor = enabled_processors.get(ext)
        content = u''
        if processor:
            fullpath = os.path.join(self.source_dir, path)
            content, ext = processor.render(fullpath, self.settings)
        else:
            if ext in text_files:
                content = self.render.to_string(path, env)
        
        return content, ext

