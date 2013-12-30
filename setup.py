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

    Authors: Anuj More, Alex Dean
    Copyright: Copyright (c) 2013-2014 Snowplow Analytics Ltd
    License: Apache License Version 2.0
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os

version_file_path = os.path.join(
    os.path.dirname(__file__),
    'snowplowtracker',
    '_version.py'
    )
exec(open(version_file_path).read(), {}, locals())

authors_list = [
    'Anuj More',
    'Alexander Dean',
    ]
authors_str = ', '.join(authors_list)

authors_email_list = [
    'anujmorex@gmail.com',
    'alex@keplarllp.com',
    ]
authors_email_str = ', '.join(authors_email_list)

setup(
    name='snowplowtracker',
    version=__version__,
    author=authors_str,
    author_email=authors_email_str,
    packages=['snowplowtracker', 'snowplowtracker.test'],
    url='http://snowplowanalytics.com',
    license='Apache License 2.0',
    description='Tracker for Snowplow Analytics.',
    long_description=open('README.rst').read(),

    install_requires = [
        "requests",
        "pycontract",
    ],
)
