import re
import copy
import json
import gzip
import mimetypes
import threading
from collections import defaultdict
import six
import requests
from requests.cookies import cookiejar_from_dict
from . import util
from . import handlers
from .contrib import bottle
from wsgiref.util import is_hop_by_hop

DEFAULT_TIMEOUT = 60
SESSION_POOL_SIZE = 10
HTTP_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')


class SessionPool(threading.local):
    def __init__(self):
        self.sess = None

    def get_session(self):
        if not self.sess:
            self.sess = requests.Session()
        self.sess.cookies = cookiejar_from_dict({})
        return self.sess

session_pool = SessionPool()


def handle_op(resp, resp_spec):
    '''
    对resp_spec中的operations各种操作进行处理.
    '''
    operations = None
    if isinstance(resp_spec.get('operations'), dict):
        operations = [resp_spec.get('operations')]
    elif isinstance(resp_spec.get('operations'), list):
        operations = resp_spec.get('operations')
    if not operations:
        return resp
    for op in operations:
        if op['type'] == 'insert_adjacent_html' and 'text/html' in (resp.content_type or ''):
            resp.body = util.dom_insert_adjacent_html(util.to_unicode(resp.body, resp.charset),
                                                      op['selector'],
                                                      op['position'],
                                                      op['html'])
            # Remove Content-Length headers in case of inconsistent length.
            if 'Content-Length' in resp.headers:
                del resp.headers['Content-Length']
    return resp


def wrap_response(resp, resp_spec):
    if isinstance(resp, six.string_types):
        resp = {'body': resp,
                'headers': {'content-type': 'text/html'}}
    if isinstance(resp, dict):
        if resp.get('headers'):
            headers_list = []
            for k, v in resp['headers'].items():
                if type(v) is set:
                    for part in v:
                        headers_list.append((k, part))
                else:
                    headers_list.append((k, v))
            resp['headers'] = headers_list
        resp = bottle.HTTPResponse(**resp)

    if isinstance(resp, bottle.HTTPResponse):
        if resp_spec.get('status'):
            resp.status = resp_spec['status']
        if resp_spec.get('headers'):
            headers = resp_spec['headers']
            if isinstance(headers, dict):
                headers = headers.items()
            for k, v in headers:
                resp.set_header(k.encode('utf-8'), v)
        resp = handle_op(resp, resp_spec)

        if 'gzip' in resp.headers.get('content-encoding', set()):
            fileobj = six.BytesIO()
            gzipper = gzip.GzipFile(fileobj=fileobj, mode='w')
            gzipper.write(util.to_bytes(resp.body, encoding=resp.charset))
            gzipper.flush()
            resp.body = fileobj.getvalue()

        return resp
    else:
        raise Exception("Unknown response type %s." % type(resp))   
    

class ModuleMock(object):
    def __init__(self, prefix, mock_file):
        self.prefix = util.format_prefix(prefix)
        self.mock = self.parse_mock_json(open(mock_file))

        def dispatch(suffix=''):
            if self.prefix == '' or self.prefix == '/':
                suffix = '/%s' % suffix
            return self.dispatch(suffix)

        common_mock = bottle.route('%s<suffix:re:.*?>' % self.prefix,
                                   method=HTTP_METHODS)(dispatch)
        root_mock = bottle.route('%s' % self.prefix,
                                 method=HTTP_METHODS)(dispatch)

    def parse_mock_json(self, fd):
        original = json.load(fd)
        result = []
        for req, resp in original:
            req_spec = {}
            if isinstance(req, six.string_types):
                if req.startswith('='):
                    req_spec['type'] = 'exact'
                    req_spec['path'] = req[1:]
                else:
                    req_spec['type'] = 'prefix'
                    req_spec['path'] = req
            elif isinstance(req, dict):
                req_spec = req
            else:
                raise ValueError("%s is not legal request spec." % req)

            if not (req_spec.get('type') and req_spec.get('path')):
                raise ValueError("The type or path of %s is neither provided nor deduced." % req)

            resp_spec = {}
            if isinstance(resp, dict):
                resp_spec = resp
            elif isinstance(resp, six.string_types):
                if resp.startswith(('http://', 'https://')):
                    resp_spec['type'] = 'remote'
                    resp_spec['url'] = resp
                else:
                    resp_spec['type'] = 'content'
                    resp_spec['headers'] = {'content-type': 'text/plain'}
                    resp_spec['body'] = resp
            else:
                raise ValueError("%s is not legal response spec." % resp)
            if resp_spec['type'] == 'remote' and not resp_spec.get('url'):
                raise ValueError("No url provided while the type of response spec is remote.") 
            if resp_spec.get('headers'):
                resp_spec['headers'] = {k.lower(): v for (k, v) in resp_spec['headers'].items()}

            result.append([req_spec, resp_spec])
        return result

    def get_mock_rule(self, req_method, req_path):
        for (req_spec, resp_spec) in self.mock:
            method = req_spec.get('method')
            if method and method != req_method:
                continue
            path = req_spec.get('path')
            if req_spec['type'] == 'exact' and path != req_path:
                continue
            elif req_spec['type'] == 'prefix' and not req_path.startswith(path):
                continue
            return (req_spec, resp_spec)
        return None

    def get_req_mock_rule(self, suffix):
        curr_req = bottle.request
        method = curr_req.method
        path = suffix
        ret = self.get_mock_rule(method, path)
        if ret is None:
            return None
        else:
            return (suffix, ret[0], ret[1])

    def get_mocked_response(self, suffix, req_spec, resp_spec):
        resp_type = resp_spec['type']
        ret = {'headers': defaultdict(set)}
        if resp_type == 'content':
            body = resp_spec.get('body') or ''
            if isinstance(body, six.string_types):
                ret['body'] = body
            else:
                ret['body'] = json.dumps(body)
                ret['headers']['content-type'] = 'application/json'
            ret['body'] = resp_spec.get('body') or ''
        elif resp_type == 'file':
            ret['body'] = open(resp_spec['body']).read()
            mime_type, __ = mimetypes.guess_type(resp_spec['body'])
            if mime_type:
                ret['headers']['content-type'] = mime_type
        elif resp_type == 'remote':
            if req_spec['type'] == 'prefix':
                pos = suffix.find(req_spec['path'])
                url = util.concat_path(resp_spec['url'], suffix[pos + len(req_spec['path']): ])
            elif req_spec['type'] == 'exact':
                url = resp_spec['url']
            else:
                raise ValueError("Unknown request type %s." % req_spec['type'])

            http_params = bottle.request.query_string
            http_body = bottle.request.body.read()
            http_method = resp_spec.get('method') or bottle.request.method or 'GET'
            http_timeout = req_spec.get('timeout') or DEFAULT_TIMEOUT
            http_headers = {k.lower(): v for k, v in util.filter_request_headers(bottle.request).items()}
            http_headers.update(req_spec.get('headers') or {})
            sess = session_pool.get_session()
            resp_obj = sess.request(http_method, url, params=http_params, data=http_body,
                                    headers=http_headers, timeout=http_timeout, allow_redirects=False)
            ret['body'] = resp_obj.content
            for k, v in resp_obj.headers.items():
                if (not is_hop_by_hop(k)) and not k.lower() in ['content-length']:
                    ret['headers'][k.lower()] = v
            if ret['headers'].get('location'):
                ret['headers']['location'] = util.replace_location_host(ret['headers']['location'],
                                                                        url, bottle.request.urlparts.netloc)
 
            set_cookie = ret['headers'].pop('set-cookie', None)
            if set_cookie:
                ret['headers']['set-cookie'] =\
                        set([i.strip() for i in re.split(r",(?![^=]+;)", set_cookie) if i.strip()])
            ret['status'] = resp_obj.status_code
        elif resp_type in handlers.HANDLERS:
            handler_object = handlers.get_handler_object(req_spec, resp_spec,
                                                         root_prefix=self.prefix)
            pos = suffix.find(req_spec['path'])
            ret = handler_object.dispatch(suffix[pos + len(req_spec['path']): ])
        else:
            raise ValueError("Unknown mock response type '%s'." % resp_type)
        return wrap_response(ret, resp_spec)

    def dispatch(self, suffix):
        mock_rule = self.get_req_mock_rule(suffix)
        if mock_rule:
            return self.get_mocked_response(*mock_rule)
        raise bottle.HTTPError(status=404)
