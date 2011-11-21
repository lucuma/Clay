# -*- coding: utf-8 -*-
"""
# Clay.static

Static files processors
"""
import os

from shake import send_file, Response

## Processors importing
## Longer but clearer than using `import_module`
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


def render(request, filepath_in, settings):
    fn, ext = os.path.splitext(filepath_in)
    processor = enabled_processors.get(ext)
    if processor is None:
        return send_file(request, filepath_in)
    
    content = processor.render(filepath_in, settings)
    return Response(content, mimetype=processor.mimetype_out)


def build(filepath_in, settings):
    fn, ext = os.path.splitext(filepath_in)
    processor = enabled_processors.get(ext)
    if processor is None:
        return
    
    filepath_out = '%s.%s' % (fn, processor.extension_out)
    processor.build(filepath_in, filepath_out, settings)
    
    file_in = os.path.split(filepath_in)[1]
    file_out = os.path.split(filepath_out)[1]
    return file_in, file_out



