#!/usr/bin/env python

sdict = {
    'name': 'ynm3k',
    'version': "0.1.1",
    'packages': ['ynm3k', 'ynm3k.contrib'],
    'scripts': ['y3k'],
    'zip_safe': False,
    'install_requires': ['requests'],
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

setup(**sdict)
