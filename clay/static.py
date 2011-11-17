"""
# Clay.static

Static files processors
"""
import os

from shake import send_file, Response

from .utils import get_source, make_file

enabled_processors = {}

try:
    from processors import clevercss_
    if clevercss_.enabled:
        for ext in clevercss_.extensions_in:
            enabled_processors[ext] = clevercss_
except ImportError:
    pass


def render_static_file(request, filepath):
    fn, ext = os.path.splitext(filepath)
    processor = enabled_processors.get(ext)
    if processor is None:
        return send_file(request, filepath)
    
    source = get_source(filepath)
    content = processor.convert(source)
    return Response(content, mimetype=processor.mimetype_out)


def make_static_file(filepath):
    fn, ext = os.path.splitext(filepath)
    processor = enabled_processors.get(ext)
    if processor is None:
        return
    
    filepath_out = '%s.%s' % (fn, processor.extension_out)
    source = get_source(filepath)
    content = processor.convert(source)
    make_file(filepath_out, content)
    
    file_in = os.path.split(filepath)[1]
    file_out = os.path.split(filepath_out)[1]
    return file_in, file_out



