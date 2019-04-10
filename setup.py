#!/usr/bin/env python

# Nordic ARC Utilities
# Copyright (C) 2019  Nordic ARC Node
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import setuptools
import narc

with open("README.md") as inf:
    long_description = inf.read()

setuptools.setup(
    name="nordic-arc-utils",
    version=narc.version,
    author="Nordic ARC",
    author_email="contact@nordic-alma.se",
    description="Various utilities for working with ALMA data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sabourke/narc_utils",
    install_requires=['python-casacore', 'numpy', 'matplotlib'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'ms-plot-freq=narc.utils:command_line_frequency_plotter',
        ],
    },
)

