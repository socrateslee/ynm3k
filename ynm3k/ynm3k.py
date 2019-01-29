import sys
import os
import signal
import argparse
import importlib
import six
import time
from .contrib import bottle
from .util import GlobCheckerThread


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=8080,
                        help="Port to bind on.")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host to bind.")
    parser.add_argument("--echo", action="store_true",
                        help="Module echo, return the current http request detail.")
    parser.add_argument("--echo-prefix", default="/_y3k/",
                        help="The path prefix for echo module")
    parser.add_argument("--mock",
                        help="Enable mocking data via a json file.")
    parser.add_argument("--mock-prefix", default="",
                        help="The path prefix for all mocking data.")
    parser.add_argument("--mock-allow-host", default=False, action="store_true",
                        help="Allow Host header to be passed into upstream servers.")
    parser.add_argument("--static", default="",
                        help="Serve static files with specified directory.")
    parser.add_argument("--static-prefix", default="/",
                        help="The path prefix for serving static files with --static.")
    parser.add_argument("--static-serve-dir", action="store_true",
                        help="Serve directories as a list.")
    parser.add_argument("--zip", default="",
                        help="Serve a zip file as static directory.")
    parser.add_argument("--zip-prefix", default="/",
                        help="The path prefix for the serving file with --zip.")   
    parser.add_argument("--zip-encoding", default="utf-8",
                        help="The encoding of zipfile")   
    parser.add_argument("--interact", action="store_true",
                        help="Attach to a interactive console.")
    parser.add_argument("--interact-path", default="/_y3k/interact",
                        help="The path for interactive console.")
    parser.add_argument("--reload", default="",
                        help="Auto reload ynm3k server when watched files matching the glob pattern changed.")
    parser.add_argument("--server", default="auto",
                        help="Specify the web server for running ynm3k, "
                        "options available at https://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend")
    parser.add_argument("--version", action='store_true', default=False,
                        help="Show version and exit.")
    args = parser.parse_args()
    return args


def run_server(args):
    if args['version']:
        from . import __VERSION__
        print("ynm3k %s" % __VERSION__)
        return
    if args['echo']:
        from . import echo
        object_echo = echo.ModuleEcho(args['echo_prefix'])
    if args['interact']:
        from . import interact
        object_interact = interact.ModuleInteract(args['interact_path'])
    if args['static']:
        from . import static
        object_static = static.ModuleStatic(args['static_prefix'],
                                            path=args['static'],
                                            serve_dir=args['static_serve_dir'])
    if args['zip']:
        from .modules import zip_serve
        object_zip = zip_serve.ModuleZipServe(args['zip_prefix'],
                                              args['zip'],
                                              args['zip_encoding'])
    if args['mock']:
        from . import mock
        object_mock = mock.ModuleMock(args['mock_prefix'], args['mock'],
                                      allow_host=args['mock_allow_host'])
    bottle.run(host=args['host'], port=int(args['port']),
               debug=True, server=args["server"])


def is_port_in_use(port):
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', port))
        sock.listen(1)
        sock.close()
    except socket.error as e:
        return True
    return False


def main():
    args = vars(parse_args())
    reload_pattern = args.pop('reload', None)
    reload_count = 0
    if not reload_pattern:
        run_server(args)
    else:
        while True:
            for i in range(3):
                if not is_port_in_use(int(args.get('port'))):
                    break
                time.sleep(0.1)
            pid = os.fork()
            if pid == 0:
                bottle.app.push()
                run_server(args)
                break
            else:
                gct = GlobCheckerThread(reload_pattern)
                gct.event_exit.clear()
                with gct:
                    try:
                        while True:
                            time.sleep(0.1)
                    except KeyboardInterrupt:
                        gct.event_exit.set()
                        if not gct.event_changed.is_set():
                            break
                        else:
                            reload_count += 1
                            print("Reloading ynm3k %s times."\
                                  % reload_count)
                            time.sleep(1.0)
                    finally:
                        os.kill(pid, signal.SIGINT)
                        os.waitpid(pid, 0)


if __name__ == '__main__':
    if six.PY2:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    main()
