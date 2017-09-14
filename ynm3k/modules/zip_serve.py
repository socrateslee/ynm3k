'''
Module for serving a zip file just like a static directory.
'''
import os
import mimetypes
import zipfile
from .. import util
from ..contrib import bottle


class ModuleZipServe(object):
    @classmethod
    def from_resp_spec(cls, req_spec, resp_spec, **kw):
        prefix = req_spec['path']
        if 'root_prefix' in kw:
            prefix = '/'.join(i for i in [kw['root_prefix'].rstrip('/'), prefix] if i)
        path = resp_spec['path']
        obj = cls(prefix, path, bind=False)
        return obj

    def __init__(self, prefix, path, bind=True):
        '''
        :param prefix: The path prefix for current route to bind with.
        :param path: The path of the zipfile in the file system.
        :param bind: (optional) Whether to bind route.
        '''
        self.prefix = util.format_prefix(prefix)
        self.path = path.rstrip('/') if path else '.'
        abs_zipfile_path = os.path.abspath(self.path)
        self.zip_obj = zipfile.ZipFile(abs_zipfile_path)
        self.zip_obj_namelist = self.zip_obj.namelist()
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
        if filename.endswith('/') or not filename:
            items = [i[len(filename):] for i in self.zip_obj_namelist if i.startswith(filename)]
            if not items:
                return bottle.HTTPError(status=404)
            ret_items = []
            for i in items:
                if '/' in i:
                    temp = i.split('/')[0] + '/'
                    if not temp in ret_items:
                        ret_items.append(temp)
                else:
                    ret_items.append(i)
            output = '<br/>'.join(map(to_dir_line,
                                      ret_items))
            return output
        if filename in self.zip_obj_namelist:
            ret = self.zip_obj.read(filename)
            mimetype, encoding = mimetypes.guess_type(filename)
            resp = bottle.HTTPResponse(body=ret)
            resp.set_header('Content-Type', mimetype)
            if encoding:
                resp.set_header('Content-Encoding', encoding)
            return resp
        else:
            return bottle.HTTPError(status=404)
