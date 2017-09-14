'''
A swtich for different types of handlers.
'''
import six
import threading

handler_lock = threading.Lock()

HANDLERS = {
    'static': {
        'module': 'ynm3k.static',
        'cls': 'ModuleStatic'
    },
    'zip': {
        'module': 'ynm3k.modules.zip_serve',
        'cls': 'ModuleZipServe'
    }
}


def get_handler_object(req_spec, resp_spec, **kw):
    handler_spec = HANDLERS[resp_spec['type']]
    if not resp_spec.get('handler'):
        with handler_lock:
            if not resp_spec.get('handler'):
                module = six._import_module(handler_spec['module'])
                cls = getattr(module, handler_spec['cls'])
                resp_spec['handler'] = cls.from_resp_spec(req_spec, resp_spec, **kw)
    return resp_spec['handler']
