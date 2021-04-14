======================================================
Python Analytics for Snowplow 
======================================================
.. image:: https://img.shields.io/static/v1?style=flat&label=Snowplow&message=Early%20Release&color=014477&labelColor=9ba0aa&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAeFBMVEVMaXGXANeYANeXANZbAJmXANeUANSQAM+XANeMAMpaAJhZAJeZANiXANaXANaOAM2WANVnAKWXANZ9ALtmAKVaAJmXANZaAJlXAJZdAJxaAJlZAJdbAJlbAJmQAM+UANKZANhhAJ+EAL+BAL9oAKZnAKVjAKF1ALNBd8J1AAAAKHRSTlMAa1hWXyteBTQJIEwRgUh2JjJon21wcBgNfmc+JlOBQjwezWF2l5dXzkW3/wAAAHpJREFUeNokhQOCA1EAxTL85hi7dXv/E5YPCYBq5DeN4pcqV1XbtW/xTVMIMAZE0cBHEaZhBmIQwCFofeprPUHqjmD/+7peztd62dWQRkvrQayXkn01f/gWp2CrxfjY7rcZ5V7DEMDQgmEozFpZqLUYDsNwOqbnMLwPAJEwCopZxKttAAAAAElFTkSuQmCC
    :alt: Early Release
    :target: https://github.com/snowplow/snowplow/wiki/Tracker-Maintenance-Classification
.. image:: https://travis-ci.org/snowplow/snowplow-python-tracker.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/snowplow/snowplow-python-tracker
.. image:: https://badge.fury.io/py/snowplow-tracker.svg
    :target: http://badge.fury.io/py/snowplow-tracker
.. image:: https://coveralls.io/repos/github/snowplow/snowplow-python-tracker/badge.svg?branch=master
    :target: https://coveralls.io/github/snowplow/snowplow-python-tracker?branch=master
.. image:: http://img.shields.io/badge/license-Apache--2-blue.svg?style=flat
    :target: http://www.apache.org/licenses/LICENSE-2.0

Release Gemfury
########
To release a new version of this package to our Gemfury instance do the following:

1 Generate the snowplow-tracker package
.. python setup.py sdist

2 Upload the package to the Gemfury instance
.. curl -f package=@dist/snowplow-tracker-X.Y.Z.tar.gz https://PUSH_TOKEN@push.fury.io/USERNAME

Where PUSH_TOKEN can be retrieved from and .. USERNAME=oda

Overview
########

Add analytics to your Python apps and Python games with the Snowplow_ event tracker for Python_.

.. _Snowplow: http://snowplowanalytics.com
.. _Python: http://python.org

With this tracker you can collect event data from your Python-based applications, games or Python web servers/frameworks.

Find out more
#############

+---------------------------------+---------------------------+-------------------------+-----------------------------------+
| Technical Docs                  | Setup Guide               | Roadmap                 | Contributing                      |
+=================================+===========================+=========================+===================================+
| |techdocs|_                     | |setup|_                  | |roadmap|               | |contributing|                    |
+---------------------------------+---------------------------+-------------------------+-----------------------------------+
| `Technical Docs`_               | `Setup Guide`_            | `Roadmap`_              | `Contributing`_                   |
+---------------------------------+---------------------------+-------------------------+-----------------------------------+

.. |techdocs| image:: https://d3i6fms1cm1j0i.cloudfront.net/github/images/techdocs.png
.. |setup| image:: https://d3i6fms1cm1j0i.cloudfront.net/github/images/setup.png
.. |roadmap| image:: https://d3i6fms1cm1j0i.cloudfront.net/github/images/roadmap.png
.. |contributing| image:: https://d3i6fms1cm1j0i.cloudfront.net/github/images/contributing.png

.. _techdocs: https://github.com/snowplow/snowplow/wiki/Python-Tracker
.. _setup: https://github.com/snowplow/snowplow/wiki/Python-Tracker-Setup

.. _`Technical Docs`: https://github.com/snowplow/snowplow/wiki/Python-Tracker
.. _`Setup Guide`: https://github.com/snowplow/snowplow/wiki/Python-Tracker-Setup
.. _`Roadmap`: https://github.com/snowplow/snowplow/wiki/Python-Tracker-Roadmap
.. _`Contributing`: https://github.com/snowplow/snowplow/wiki/Python-Tracker-Contributing

Quickstart
#######################

Assuming pyenv_ is installed

::

   host$ git clone git@github.com:snowplow/snowplow-python-tracker.git
   host$ cd snowplow-python-tracker
   host$ pyenv install 2.7.18 && pyenv install 3.5.10 && pyenv install 3.6.12 && pyenv install 3.7.9 && pyenv install 3.8.6 && pyenv install 3.9.0
   host$ ./run-tests.sh deploy
   host$ ./run-tests.sh test

.. _pyenv: https://github.com/pyenv/pyenv

Copyright and license
#####################

The Snowplow Python Tracker is copyright 2013-2020 Snowplow Analytics Ltd.

Licensed under the `Apache License, Version 2.0`_ (the "License");
you may not use this software except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
