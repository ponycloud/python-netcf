#!/usr/bin/python -tt

from setuptools import setup

setup(
    name = 'python-netcf',
    version = '1',
    author = 'The PonyCloud Team',
    description = ('NetCF bindings'),
    license = 'proprietary',
    keywords = 'network',
    url = 'http://github.com/ponycloud/python-netcf',
    packages=['netcf'],
    long_description='''
Python bindings for the NetCF library.

The NetCF library provides relatively high-level API to configuration of
Linux network interfaces. Since sometimes it is useful to be able to plug
into this interface without NetworkManager or libvirt, we bring you these
simple bindings based on python-ctypes.
''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: System :: Networking',
        'License :: Other/Proprietary License',
    ],
)


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
