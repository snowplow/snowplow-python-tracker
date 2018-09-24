"""
    setup.py

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
    'Fred Blundun'
    ]
authors_str = ', '.join(authors_list)

authors_email_list = [
    'support@snowplowanalytics.com',
    ]
authors_email_str = ', '.join(authors_email_list)

setup(
    name='snowplow-tracker',
    version='0.8.1rc1.dev1',
    author=authors_str,
    author_email=authors_email_str,
    packages=['snowplow_tracker', 'snowplow_tracker.test'],
    url='http://snowplowanalytics.com',
    license='Apache License 2.0',
    description='Snowplow event tracker for Python. Add analytics to your Python and Django apps, webapps and games',
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
        "Operating System :: OS Independent",
    ],

    install_requires=[
        "greenlet>=0.4.10,<1.0.0",
        "requests>=2.2.1,<3.0.0",
        "pycontracts>=1.7.6,<2.0.0",
        "celery>=3.1.11,<4.0.0",
        "gevent>=1.0.2,<2.0.0",
        "redis>=2.9.1,<3.0.0",
        "six>=1.9.0,<2.0.0"
    ],
)
