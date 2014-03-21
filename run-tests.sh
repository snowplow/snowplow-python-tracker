#!/bin/sh
# Run the Snowplow Tracker test suite.

# Need to execute from this dir
cd $(dirname $0)

# pytest because it has a neat output
/vagrant/snowplow-python-tracker-environment/bin/python3.3 -m pytest -s
