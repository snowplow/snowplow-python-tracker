Python Analytics for Snowplow
=============================

[![Early Release](https://img.shields.io/static/v1?style=flat&label=Snowplow&message=Early%20Release&color=014477&labelColor=9ba0aa&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAeFBMVEVMaXGXANeYANeXANZbAJmXANeUANSQAM+XANeMAMpaAJhZAJeZANiXANaXANaOAM2WANVnAKWXANZ9ALtmAKVaAJmXANZaAJlXAJZdAJxaAJlZAJdbAJlbAJmQAM+UANKZANhhAJ+EAL+BAL9oAKZnAKVjAKF1ALNBd8J1AAAAKHRSTlMAa1hWXyteBTQJIEwRgUh2JjJon21wcBgNfmc+JlOBQjwezWF2l5dXzkW3/wAAAHpJREFUeNokhQOCA1EAxTL85hi7dXv/E5YPCYBq5DeN4pcqV1XbtW/xTVMIMAZE0cBHEaZhBmIQwCFofeprPUHqjmD/+7peztd62dWQRkvrQayXkn01f/gWp2CrxfjY7rcZ5V7DEMDQgmEozFpZqLUYDsNwOqbnMLwPAJEwCopZxKttAAAAAElFTkSuQmCC)](https://docs.snowplow.io/docs/collecting-data/collecting-from-own-applications/tracker-maintenance-classification/)[![Build Status](https://github.com/snowplow/snowplow-python-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/snowplow/snowplow-python-tracker/actions)[![Test Coverage](https://img.shields.io/coveralls/github/snowplow/snowplow-python-tracker)](https://coveralls.io/github/snowplow/snowplow-python-tracker?branch=master) [![image](http://img.shields.io/badge/license-Apache--2-blue.svg?style=flat)](http://www.apache.org/licenses/LICENSE-2.0)


[![Pypi Snowplow Tracker](https://img.shields.io/pypi/v/snowplow-tracker)](https://pypi.org/project/snowplow-tracker/)[![Python Versions](https://img.shields.io/pypi/pyversions/snowplow-tracker)](https://pypi.org/project/snowplow-tracker/)[![Monthly Downloads](https://img.shields.io/pypi/dm/snowplow-tracker)](https://pypi.org/project/snowplow-tracker/)

Overview
--------

Add analytics to your Python apps and Python games with the
[Snowplow](http://snowplow.io) event tracker for
[Python](http://python.org).

With this tracker you can collect event data from your Python-based
applications, games or Python web servers/frameworks.

Find out more
-------------

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

  | Snowplow Docs | API Docs  | Contributing |
  |     :----:     |     :----:   |     :----:   |
  | ![techdocs](https://d3i6fms1cm1j0i.cloudfront.net/github/images/techdocs.png) | ![setup](https://d3i6fms1cm1j0i.cloudfront.net/github/images/setup.png) |                                                ![contributing](https://d3i6fms1cm1j0i.cloudfront.net/github/images/contributing.png) |
  | [Snowplow Docs](https://docs.snowplow.io/docs/collecting-data/collecting-from-own-applications/python-tracker/) | [API Docs](https://snowplow.github.io/snowplow-python-tracker/index.html)| [Contributing](https://github.com/snowplow/snowplow-python-tracker/blob/master/CONTRIBUTING.md) |                                                                              
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Python Support
--------------

| Python version | snowplow-tracker version |
|     :----:     |     :----:               |
| \>=3.8         | > 1.1.0                 |
| \>=3.5         | > 0.10.0                 |
| 2.7            | > 0.9.1                  |

Maintainer Quickstart
---------------------

Assuming [docker](https://www.docker.com/) is installed

    host$ git clone git@github.com:snowplow/snowplow-python-tracker.git
    host$ cd snowplow-python-tracker
    host$ docker build -t snowplow-python-tracker . && docker run snowplow-python-tracker

Copyright and license
---------------------

The Snowplow Python Tracker is copyright 2013-2023 Snowplow Analytics
Ltd.

Licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0) (the \"License\"); you
may not use this software except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
