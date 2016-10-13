#!/usr/bin/env python


import os
from os.path import expanduser
import sys

from release_manager import utils, logger

from snowplow_tracker import _version

# --- Constants


HOME = expanduser("~")
DEFAULT_SERVER = 'https://pypi.python.org/pypi'
DEFAULT_REPO = 'pypi'
PYPIRC_FILE = '%s/.pypirc' % HOME

if 'TRAVIS_TAG' in os.environ:
    TRAVIS_TAG = os.environ.get('TRAVIS_TAG')
else:
    sys.exit("Environment variable TRAVIS_TAG is unavailable")

if 'TRAVIS_BUILD_DIR' in os.environ:
    TRAVIS_BUILD_DIR = os.environ.get('TRAVIS_BUILD_DIR')
else:
    sys.exit("Environment variable TRAVIS_BUILD_DIR is unavailable")

if 'PYPI_PASSWORD' in os.environ:
    PYPI_PASSWORD = os.environ.get('PYPI_PASSWORD')
else:
    sys.exit("Environment variable PYPI_PASSWORD is unavailable")


# --- Helpers


def check_version():
    """Fail deploy if tag version doesn't match version"""
    logger.log_start("Checking versions")
    if TRAVIS_TAG != _version.__build_version__:
        sys.exit("Version extracted from project doesn't match the TRAVIS_TAG variable. TRAVIS_TAG: {}, __build_version__: {}!".format(TRAVIS_TAG, _version.__build_version__))
    else:
        logger.log_info("Versions match!")
        logger.log_done()


def write_config():
    """Writes an array of lines to the PyPi config file"""
    logger.log_start("Writing ~/.pypirc file")
    lines = [
        '[distutils]\n',
        'index-servers =\n',
        '  %s\n' % DEFAULT_REPO,
        '\n',
        '[%s]\n' % DEFAULT_REPO,
        'repository=%s\n' % DEFAULT_SERVER,
        'username=snowplow\n',
        'password=%s\n' % PYPI_PASSWORD
    ]

    with open(PYPIRC_FILE, 'w') as outfile:
        for line in lines:
            outfile.write(line)
    logger.log_info("The ~/.pypirc file has been written!")
    logger.log_done()


def deploy_to_pypi():
    """Deploys the release to PyPi"""
    logger.log_start("Deploying to PyPi")
    os.chdir(TRAVIS_BUILD_DIR)
    utils.execute("python setup.py register -r pypi", shell=True)
    utils.execute("python setup.py sdist upload -r pypi", shell=True)
    logger.log_info("Module deployed to PyPi!")
    logger.log_done()


# --- Main


if __name__ == "__main__":
    logger.log_header("Deploying snowplow-python-tracker to PyPi")
    check_version()
    write_config()
    deploy_to_pypi()
    logger.log_footer("Deployed version %s to PyPi!" % TRAVIS_TAG)
