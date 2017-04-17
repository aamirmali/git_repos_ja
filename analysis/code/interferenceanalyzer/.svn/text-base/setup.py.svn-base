"""This module sets up the intanalyzer module. Before using this, read INSTALL.
You should be able to use the pre-compiled binaries, without ever needing to
use this module."""
from distutils.core import setup, Extension

module = Extension('intanalyzer',
                    sources = ['pythonmodule.c','interferenceanalyzer.c'])

setup (name = 'Interference Analyzer',
       version = '1.000',
       description = 'This module calculates interference patterns',
       ext_modules=[module])
