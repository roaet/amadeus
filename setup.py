#!/usr/local/env python

import setuptools

setuptools.setup(
    setup_requires=['pbr'],
    packages=setuptools.find_packages(),
    pbr=True,
)
