"""
    setup.py

    Copyright (c) 2018 Fishtown Analytics LLC.
    Copyright (c) 2013-2014 Snowplow Analytics Ltd. All rights reserved.

    This program is licensed to you under the Apache License Version 2.0,
    and you may not use this file except in compliance with the Apache License
    Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
    http://www.apache.org/licenses/LICENSE-2.0.

    Unless required by applicable law or agreed to in writing,
    software distributed under the Apache License Version 2.0 is distributed on
    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied. See the Apache License Version 2.0 for the specific
    language governing permissions and limitations there under.

    Authors: Anuj More, Alex Dean, Fred Blundun
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

version_file_path = os.path.join(
    os.path.dirname(__file__),
    'snowplow_tracker',
    '_version.py'
    )
exec(open(version_file_path).read(), {}, locals())

authors_list = [
    'Anuj More',
    'Alexander Dean',
    'Fred Blundun',
    'Drew Bannin',
    'Jacob Beck'
]
authors_str = ', '.join(authors_list)

setup(
    name='minimal-snowplow-tracker',
    version=__version__,
    author=authors_str,
    packages=['snowplow_tracker', 'snowplow_tracker.test'],
    url='https://www.fishtownanalytics.com',
    license='Apache License 2.0',
    description='A minimal snowplow event tracker for Python. Add analytics to your Python and Django apps, webapps and games',
    long_description=open('README.rst').read(),

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        "requests>=2.2.1,<3.0",
        "pycontracts>=1.7.6,<2.0",
        "six>=1.9.0,<2.0"
    ],
)
