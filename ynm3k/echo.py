'''
Echo the http request context.
'''
from . import util
from .contrib import bottle


def get_request_dict():
    d = dict()
    d.update({str(k): str(v) for k, v in list(bottle.request.environ.items())})
    return d


class ModuleEcho(object):
    def __init__(self, prefix):
        self.prefix = util.format_prefix(prefix)

        @bottle.route('%secho.json' % self.prefix)
        def echo():
            return get_request_dict()
