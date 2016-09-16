======================================================
Python Analytics for Snowplow 
======================================================
.. image:: https://travis-ci.org/snowplow/snowplow-python-tracker.png?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/snowplow/snowplow-python-tracker
.. image:: https://badge.fury.io/py/snowplow-tracker.png
    :target: http://badge.fury.io/py/snowplow-tracker
.. image:: https://coveralls.io/repos/snowplow/snowplow-python-tracker/badge.png
    :target: https://coveralls.io/r/snowplow/snowplow-python-tracker
.. image:: http://img.shields.io/badge/license-Apache--2-blue.svg?style=flat
    :target: http://www.apache.org/licenses/LICENSE-2.0


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

Contributing quickstart
#######################

Assuming Git, Vagrant_ and VirtualBox_ are installed:

::

   host$ git clone git@github.com:snowplow/snowplow-python-tracker.git
   host$ vagrant up && vagrant ssh
  guest$ cd /vagrant
  guest$ ./run-tests.sh deploy
  guest$ ./run-tests.sh test

.. _Vagrant: http://docs.vagrantup.com/v2/installation/index.html
.. _VirtualBox: https://www.virtualbox.org/wiki/Downloads

Publishing
##########

::

   host$ vagrant push

Copyright and license
#####################

The Snowplow Python Tracker is copyright 2013-2014 Snowplow Analytics Ltd.

Licensed under the `Apache License, Version 2.0`_ (the "License");
you may not use this software except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
