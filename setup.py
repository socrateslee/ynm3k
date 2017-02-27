#!/usr/bin/env python
from ynm3k import __VERSION__

sdict = {
    'name': 'ynm3k',
    'version': __VERSION__,
    'packages': ['ynm3k', 'ynm3k.contrib'],
    'scripts': ['y3k'],
    'zip_safe': False,
    'install_requires': ['six', 'requests'],
    'author': 'Lichun',
    'classifiers': [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python']
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if __name__ == '__main__':
    setup(**sdict)
