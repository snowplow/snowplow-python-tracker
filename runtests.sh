#!/bin/sh
# Run the Snowplow Tracker test suite.

cd $(dirname $0)

# "python -m" differs from "python snowplow/test/runtests.py" in how it sets
# up the default python path.  "python -m" uses the current directory,
# while "python file.py" uses the directory containing "file.py" (which is
# not what you want if file.py appears within a package you want to import
# from)

# python -m snowplowtracker.test.runtests "$@"
# nosetests
python -m pytest -s
