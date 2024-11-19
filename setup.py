#
#     setup.py

#     Copyright (c) 2013-2023 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.
# """

#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

authors_list = [
    "Anuj More",
    "Alexander Dean",
    "Fred Blundun",
    "Paul Boocock",
    "Matus Tomlein",
    "Jack Keene",
]
authors_str = ", ".join(authors_list)

authors_email_list = [
    "support@snowplow.io",
]
authors_email_str = ", ".join(authors_email_list)

setup(
    name="snowplow-tracker",
    version="1.0.3",
    author=authors_str,
    author_email=authors_email_str,
    packages=["snowplow_tracker", "snowplow_tracker.test", "snowplow_tracker.events"],
    package_data={"snowplow_tracker": ["py.typed"]},
    url="http://snowplow.io",
    license="Apache License 2.0",
    description="Snowplow event tracker for Python. Add analytics to your Python and Django apps, webapps and games",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests>=2.25.1,<3.0",
        "types-requests>=2.25.1,<3.0",
        "typing_extensions>=3.7.4",
    ],
)
