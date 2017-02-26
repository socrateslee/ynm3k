'''
Interact module
---------------
An Interactive console of a request.
'''
import os
import sys
import code
from .contrib import bottle


class ModuleInteract(object):
    def __init__(self, path):
        @bottle.route(path)
        def interact():
            backup_stdin = os.dup(sys.stdin.fileno())
            os.dup2(sys.stdout.fileno(), sys.stdin.fileno())
            code.interact(local=globals(), banner=u'Ctrl + D to detach.')
            os.dup2(backup_stdin, sys.stdin.fileno())
            return ''
