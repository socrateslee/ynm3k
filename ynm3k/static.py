'''
Basic module for serving static files in current directory.
'''
import os
from . import util
from .contrib import bottle


class ModuleStatic(object):
    @classmethod
    def from_resp_spec(cls, req_spec, resp_spec, **kw):
        prefix = req_spec['path']
        if 'root_prefix' in kw:
            prefix = '/'.join(i for i in [kw['root_prefix'].rstrip('/'), prefix] if i)
        path = resp_spec['path']
        serve_dir = resp_spec.get("serve_dir", False)
        try_files = resp_spec.get("try_files")
        obj = cls(prefix, path, serve_dir=serve_dir, try_files=try_files, bind=False)
        return obj

    def __init__(self, prefix, path, serve_dir=False, try_files=None, bind=True):
        self.prefix = util.format_prefix(prefix)
        self.path = path.rstrip('/') if path else '.'
        self.serve_dir = serve_dir
        if not try_files:
            try_files = []
        try_files = try_files if isinstance(try_files, list) else [try_files]
        self.try_files = try_files
        if bind:
            self.bind()

    def bind(self):
        root_static = bottle.route(self.prefix)(self.dispatch)
        common_static = bottle.route('%s<filename:path>' % self.prefix)(self.dispatch)

    def dispatch(self, filename=''):
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
        ret = None
        if (self.prefix + filename).endswith('/'):
            for suffix in self.try_files:
                curr_filename = filename + suffix
                curr_path = os.path.abspath(self.path) + os.sep + curr_filename
                if os.path.exists(curr_path):
                    ret = bottle.static_file(curr_filename, root=os.path.abspath(self.path))
                    break
        if ret is None:
            ret = bottle.static_file(filename, root=os.path.abspath(self.path))
        return ret
