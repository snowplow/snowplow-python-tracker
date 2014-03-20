#!/bin/sh
# Run the Snowplow Tracker test suite.

cd $(dirname $0)

# Run any one of the following three commands.
# Personally I prefer pytest because it has a neat output but travis-ci uses
# nosetests. The choice of choosing nosetests or pytest should not make a
# difference to the way tests are run (a test failing under nosetests *will*
# fail under pytests and the other way round).

/vagrant/snowplow-python-tracker-environment/bin/python3.3 -m pytest -s
