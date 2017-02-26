'''
Basic module for serving static files in current directory.
'''
import os
from . import util
from .contrib import bottle


class ModuleStatic(object):
    def __init__(self, prefix, path, serve_dir=False):
        self.prefix = util.format_prefix(prefix)
        self.path = os.path.dirname(path if path else '.')
        self.serve_dir = serve_dir

        def server_static(filename=''):
            def to_dir_line(item):
                item_path = '%s%s' % (filename, item) if filename.endswith('/') or not filename\
                            else '%s/%s' % (filename, item)
                return "<a href='%s%s'>%s</a>" % (self.prefix, item_path, item)
            abs_path = os.path.abspath(self.path) + "/" + filename
            if self.serve_dir\
                    and os.path.exists(abs_path) and os.path.isdir(abs_path)\
                    and '/./' not in abs_path and '/../' not in abs_path:
                output = '<br/>'.join(map(to_dir_line,
                                          os.listdir(abs_path)))
                return output
            return bottle.static_file(filename, root=os.path.abspath(self.path))

        root_static = bottle.route(self.prefix)(server_static)
        common_static = bottle.route('%s<filename:path>' % self.prefix)(server_static)
