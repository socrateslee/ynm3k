import copy
import json
import gzip
import mimetypes
import six
import requests
from . import util
from .contrib import bottle
from wsgiref.util import is_hop_by_hop

DEFAULT_TIMEOUT = 60
SESSION_POOL_SIZE = 10
HTTP_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')


class SessionPool(object):
    def __init__(self, size=None):
        self.size = SESSION_POOL_SIZE if size is None else size
        self.pool = [None] * self.size

    def get_session(self):
        user_agent = bottle.request.environ.get('HTTP_USER_AGENT') or ''
        remote_addr = bottle.request.environ.get('REMOTE_ADDR') or ''
        idx = hash("%s%s" % (user_agent, remote_addr)) % self.size
        if not self.pool[idx]:
            self.pool[idx] = requests.Session()
        return self.pool[idx]

session_pool = SessionPool()


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
        ret = {}
        if resp_type == 'content':
            body = resp_spec.get('body') or ''
            if isinstance(body, six.string_types):
                ret['body'] = body
            else:
                ret['body'] = json.dumps(body)
                ret['headers'] = {'content-type': 'application/json'}
            ret['body'] = resp_spec.get('body') or ''
        elif resp_type == 'file':
            ret['body'] = open(resp_spec['body']).read()
            mime_type, __ = mimetypes.guess_type(resp_spec['body'])
            if mime_type:
                ret['headers'] = {'content-type': mime_type}
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
            ret['headers'] = dict([(k.lower(), v) for k, v in resp_obj.headers.items()\
                                    if (not is_hop_by_hop(k)) and not k.lower() in ['content-length']])
            ret['status'] = resp_obj.status_code
            if ret['headers'].get('content-encoding') == 'gzip':
                fileobj = six.BytesIO()
                gzipper = gzip.GzipFile(fileobj=fileobj, mode='w')
                gzipper.write(resp_obj.content)
                gzipper.flush()
                ret['body'] = fileobj.getvalue()
        else:
            raise ValueError("Unknown mock response type '%s'." % resp_type)

        ret['status'] = ret['status'] if 'status' in ret else 200
        ret['headers'] = ret['headers'] if 'headers' in ret else {}
        if resp_spec.get('headers'):
            ret['headers'].update(resp_spec['headers'])
        if not ret['headers'].get('content-type'):
            ret['headers']['content-type'] = 'text/plain'
        ret['headers'] = {k.encode('utf-8') if isinstance(k, six.text_type) else k: v\
                          for k, v in ret['headers'].items()}
        return bottle.HTTPResponse(**ret)

    def dispatch(self, suffix):
        mock_rule = self.get_req_mock_rule(suffix)
        if mock_rule:
            return self.get_mocked_response(*mock_rule)
        raise bottle.HTTPError(status=404)
