#!/bin/sh
# Run the Snowplow Tracker test suite.

# Need to execute from this dir
cd $(dirname $0)

# pytest because it has a neat output

/vagrant/snowplow-python-3.3-tracker-environment/bin/python3.3 -m pytest -s

/vagrant/snowplow-python-2.7-tracker-environment/bin/python2.7 -m pytest -s
