'''
utility functions.
'''
from wsgiref.util import is_hop_by_hop
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


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


def replace_location_host(location, upstream, request_host):
    parsed_location = urlparse(location)
    parsed_upstream = urlparse(upstream)
    if parsed_location.netloc and parsed_upstream.netloc\
            and parsed_location.scheme == parsed_upstream.scheme\
            and parsed_upstream.netloc.lower() in parsed_location.netloc.lower():
        return location.lower().replace(parsed_upstream.netloc.lower(),
                                        request_host)
    else:
        return location


def concat_path(*parts):
    ret = ''
    for i in parts:
        if ret.endswith('/') and i.startswith('/'):
            ret = ret[:-1] + i
        else:
            ret = ret + i
    return ret
