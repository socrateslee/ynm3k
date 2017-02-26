'''
utility functions.
'''
from wsgiref.util import is_hop_by_hop


def format_prefix(prefix):
    '''
    Format url path prefix, ensure '/' in the begining.
    '''
    prefix = '' if prefix is None else prefix
    prefix = prefix if prefix.startswith('/') else '/%s' % prefix
    return prefix


def filter_request_headers(req):
    ret = [(k, v) for (k, v) in req.headers.items()\
           if not is_hop_by_hop(k)]
    remove_headers = ['content-length', 'host']
    ret = dict(filter(lambda x: x[0].lower() not in remove_headers,
                      ret))
    return ret


def concat_path(*parts):
    ret = ''
    for i in parts:
        if ret.endswith('/') and i.startswith('/'):
            ret = ret[:-1] + i
        else:
            ret = ret + i
    return ret
