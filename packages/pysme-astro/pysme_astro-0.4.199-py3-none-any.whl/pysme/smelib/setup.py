# -*- coding: utf-8 -*-
from distutils.core import Extension, setup
from os.path import abspath, dirname, join

import numpy
from libtools import get_full_libfile

libdir = get_full_libfile()
libdir = abspath(dirname(libdir))
include_dirs = [numpy.get_include()]
include_dirs += [libdir]

module = Extension(
    "_smelib",
    sources=["_smelib.cpp"],
    language="c++",
    include_dirs=include_dirs,
    libraries=["sme"],
    library_dirs=[libdir],
)

setup(ext_modules=[module])
