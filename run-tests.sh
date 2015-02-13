#!/bin/sh
# Run the Snowplow Tracker test suite.

# Quit on failure
set -e

# Need to execute from this dir
cd $(dirname $0)

# pytest because it has a neat output

# Test against Python 3
~/snowplow-python-3.3-tracker-environment/bin/python3.3 -m pytest -s

# Test against Python 2
~/snowplow-python-2.7-tracker-environment/bin/python2.7 -m pytest -s

