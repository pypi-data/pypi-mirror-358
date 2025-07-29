# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 10:46:24 2024

@author: Giriyan
"""


# This file is part of sir3stoolkit.
from setuptools import setup, find_packages


setup(
    name='sir3stoolkit',
    version='90.15.0.1.dev1',
    description='SIR3S Toolkit',
    long_description='SIR3S Python Toolkit',
    author="3S Consult GmbH",
    author_email="giriyan@3sconsult.de",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.9, <4',
    install_requires=['numpy',
                      'pythonnet',
                      ],
)
