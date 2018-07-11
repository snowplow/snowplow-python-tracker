======================================================
Python Analytics for Snowplow 
======================================================
.. image:: https://circleci.com/gh/fishtown-analytics/snowplow-python-tracker/tree/master.svg?style=svg
	:alt: Build Status
	:target: https://circleci.com/gh/fishtown-analytics/snowplow-python-tracker


Overview
########

Add analytics to your Python apps and Python games with the Snowplow_ event tracker for Python_.

.. _Snowplow: http://snowplowanalytics.com
.. _Python: http://python.org

With this tracker you can collect event data from your Python-based applications, games or Python web servers/frameworks.

This is a fork of the original Snowplow Python tracker v0.8.0, with a number of changes:
	- All emitters except for the basic one removed
	- Tests converted to docker
	- All tracking event methods except for structured/unstructured removed
	- Python 3.7 supported


Contributing quickstart
#######################

Assuming Git and Docker_ (with docker-compose) are installed:

::

   host$ git clone git@github.com:snowplow/snowplow-python-tracker.git
   host$ docker-compose run --rm test tox

.. _Docker: https://www.docker.com/community-edition

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

This software has been modified by Fishtown Analytics. Changes are copyright 2018 Fishtown Analytics LLC.

.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
