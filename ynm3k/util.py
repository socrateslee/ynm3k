# coding: utf-8
'''
utility functions.
'''
from wsgiref.util import is_hop_by_hop
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
try:
    import _thread as thread
except ImportError:
    import thread
import threading
import time
import os
import glob
import six


def format_prefix(prefix):
    '''
    Format url path prefix, ensure '/' in the begining.
    '''
    prefix = '' if prefix is None else prefix
    prefix = prefix if prefix.startswith('/') else '/%s' % prefix
    return prefix


def filter_request_headers(req, allow_host=False):
    ret = [(k, v) for (k, v) in req.headers.items()\
           if not is_hop_by_hop(k)]
    if allow_host:
        remove_headers = ['content-length']
    else:
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


def to_unicode(content, encoding='utf-8'):
    if hasattr(content, 'read'):
        content = content.read()
    if not isinstance(content, six.text_type):
        content = content.decode(encoding, 'ignore')
    return content


def to_bytes(content, encoding='utf-8'):
    if isinstance(content, six.text_type):
        content = content.encode(encoding, 'ignore')
    return content


def insert_adjacent_html(element, position, html):
    import bs4
    new_element = bs4.BeautifulSoup(html, 'html.parser')
    if position == "beforebegin":
        element.insert_before(new_element)
    elif position == "afterbegin":
        element.insert(0, new_element)
    elif position == "beforeend":
        element.append(new_element)
    elif position == "afterend":
        element.insert_after(new_element)
    else:
        pass


def dom_insert_adjacent_html(dom_html, selector, position, html):
    '''
    对于在dom_html中，通过selector选定的标签，在指定的position中插入的html。
    此方法的机制类似于js中的insertAdjacentHTML方法，
    参考 https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML
    '''
    import bs4
    dom = bs4.BeautifulSoup(dom_html, 'html.parser')
    for element in dom.select(selector):
        insert_adjacent_html(element, position, html)
    return str(dom)


class GlobCheckerThread(threading.Thread):
    '''
    A thread to checking the change event of the given glob patterns.
    '''
    def __init__(self, glob_pattern, interval=1, callback=None):
        threading.Thread.__init__(self)
        self.glob_pattern = glob_pattern
        self.interval = interval
        if callback:
            self.callback = callback
        else:
            def default_callback():
                thread.interrupt_main()
                return True
            self.callback = default_callback
        self.files = self._get_files()
        self.event_changed = threading.Event()
        self.event_exit = threading.Event()

    def _get_files(self):
        files = dict()
        for path in glob.iglob(self.glob_pattern):
            files[path] = os.stat(path).st_mtime
        return files

    def run(self):
        try:
            while not self.event_exit.is_set():
                changed = False
                new_files = self._get_files()
                for path, mtime in self.files.items():
                    if new_files.get(path) != mtime:
                        changed = True
                        break
                if not changed:
                    if set(new_files.keys()) - set(self.files.keys()):
                        changed = True
                if changed:
                    self.event_changed.set()
                    if self.callback():
                        break
                self.files = new_files
                time.sleep(self.interval)
        except KeyboardInterrupt as e:
            print("KeyboardInterrupt in the glob checking loop.")
        except Exception as e:
            pass

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()
        return exc_type is not None and issubclass(exc_type, KeyboardInterrupt)
