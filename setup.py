"""
    setup.py

    Copyright (c) 2013-2021 Snowplow Analytics Ltd. All rights reserved.

    This program is licensed to you under the Apache License Version 2.0,
    and you may not use this file except in compliance with the Apache License
    Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
    http://www.apache.org/licenses/LICENSE-2.0.

    Unless required by applicable law or agreed to in writing,
    software distributed under the Apache License Version 2.0 is distributed on
    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
    express or implied. See the Apache License Version 2.0 for the specific
    language governing permissions and limitations there under.

    Authors: Anuj More, Alex Dean, Fred Blundun, Paul Boocock
    Copyright: Copyright (c) 2013-2021 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

authors_list = [
    'Anuj More',
    'Alexander Dean',
    'Fred Blundun',
    'Paul Boocock',
    'Matt Miermans'
]
authors_str = ', '.join(authors_list)

authors_email_list = [
    'm.miermans@gmail.com',
]
authors_email_str = ', '.join(authors_email_list)

setup(
    name='aio-snowplow-tracker',
    version='1.0.0.a1',
    author=authors_str,
    author_email=authors_email_str,
    packages=['snowplow_tracker', 'snowplow_tracker.test', 'snowplow_tracker.redis', 'snowplow_tracker.celery'],
    url='https://github.com/miermans/aio-snowplow-python-tracker',
    license='Apache License 2.0',
    description='Asyncio Snowplow event tracker for Python. '
                'Add analytics to your Python and Django apps, webapps and games',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        "requests>=2.25.1,<3.0",
        "typing_extensions>=3.7.4"
    ],

    extras_require={
        "celery": [
            "celery>=4.0,<5.0;python_version<'3.0'",
            "celery>=4.0;python_version>='3.0'"
        ],
        "redis": [
            "redis>=2.9.1,<4.0;python_version<'3.0'",
            "redis>=2.9.1;python_version>='3.0'",
            "gevent>=21.1.2"
        ]
    },
)
