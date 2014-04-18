import os
import glob

try:
    from setuptools import setup, find_packages, Command
    packagedata = True
except ImportError:
    from distutils.core import setup
    from distutils.cmd import Command
    packagedata = False

    def find_packages(path='steelscript'):
        return [p for p, files, dirs in os.walk(path) if '__init__.py' in files]

from versioning import get_version

setup_args = {
    'name':               'steelscript.netshark',
    'namespace_packages': ['steelscript'],
    'version':            get_version(),
    'author':             'Riverbed Technology',
    'author_email':       'cwhite@riverbed.com',
    'url':                'http://pythonhosted.org/steelscript',
    'description':        'Python module for interacting with Riverbed Shark with SteelScript',

    'long_description': '''SteelScript for NetShark
========================

SteelScript is a collection of libraries and scripts in Python and JavaScript for
interacting with Riverbed Technology devices.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/install.html
    ''',

    'platforms': 'Linux, Mac OS, Windows',

    'classifiers': (
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
    ),

    'packages': find_packages(),

    'scripts': (
        'utilities/shark_view_fields.py',
    ),

    'install_requires': (
        'steelscript.common>=0.6',
    ),
}

if packagedata:
    setup_args['include_package_data'] = True

setup(**setup_args)
