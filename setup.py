#!/usr/bin/env python
from ynm3k import __VERSION__

long_description = ""

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    pass

sdict = {
    'name': 'ynm3k',
    'version': __VERSION__,
    'packages': ['ynm3k',
                 'ynm3k.contrib',
                 'ynm3k.modules'],
    'scripts': ['y3k'],
    'zip_safe': False,
    'install_requires': ['six', 'requests'],
    'author': 'Lichun',
    'long_description': long_description,
    'url': 'https://github.com/socrateslee/ynm3k',
    'classifiers': [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python']
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if __name__ == '__main__':
    setup(**sdict)
