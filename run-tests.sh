#!/bin/bash

# Run the Snowplow Tracker test suite.

# Quit on failure
set -e

# Need to execute from this dir
cd $(dirname $0)

# pytest because it has a neat output

export PATH="~/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

function deploy {
  # pyenv install 3.5.10
  if [ ! -e ~/.pyenv/versions/tracker35 ]; then
    pyenv virtualenv 3.5.10 tracker35
    pyenv activate tracker35
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -e ~/.pyenv/versions/tracker35redis ]; then
    pyenv virtualenv 3.5.10 tracker35redis
    pyenv activate tracker35redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.6.14
  if [ ! -e ~/.pyenv/versions/tracker36 ]; then
    pyenv virtualenv 3.6.14 tracker36
    pyenv activate tracker36
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -e ~/.pyenv/versions/tracker36redis ]; then
    pyenv virtualenv 3.6.14 tracker36redis
    pyenv activate tracker36redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.7.11
  if [ ! -e ~/.pyenv/versions/tracker37 ]; then
    pyenv virtualenv 3.7.11 tracker37
    pyenv activate tracker37
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -e ~/.pyenv/versions/tracker37redis ]; then
    pyenv virtualenv 3.7.11 tracker37redis
    pyenv activate tracker37redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.8.11
  if [ ! -e ~/.pyenv/versions/tracker38 ]; then
    pyenv virtualenv 3.8.11 tracker38
    pyenv activate tracker38
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -e ~/.pyenv/versions/tracker38redis ]; then
    pyenv virtualenv 3.8.11 tracker38redis
    pyenv activate tracker38redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.9.6
  if [ ! -e ~/.pyenv/versions/tracker39 ]; then
    pyenv virtualenv 3.9.6 tracker39
    pyenv activate tracker39
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -e ~/.pyenv/versions/tracker39redis ]; then
    pyenv virtualenv 3.9.6 tracker39redis
    pyenv activate tracker39redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.10.1
  if [ ! -e ~/.pyenv/versions/tracker310 ]; then
    pyenv virtualenv 3.10.1 tracker310
    pyenv activate tracker310
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -e ~/.pyenv/versions/tracker310redis ]; then
    pyenv virtualenv 3.10.1 tracker310redis
    pyenv activate tracker310redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.11.0
  if [ ! -e ~/.pyenv/versions/tracker311 ]; then
    pyenv virtualenv 3.11.0 tracker311
    pyenv activate tracker311
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -e ~/.pyenv/versions/tracker311redis ]; then
    pyenv virtualenv 3.11.0 tracker311redis
    pyenv activate tracker311redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi
}


function run_tests {
  pyenv activate tracker35
  pytest
  source deactivate

  pyenv activate tracker35redis
  pytest
  source deactivate

  pyenv activate tracker36
  pytest
  source deactivate

  pyenv activate tracker36redis
  pytest
  source deactivate

  pyenv activate tracker37
  pytest
  source deactivate

  pyenv activate tracker37redis
  pytest
  source deactivate

  pyenv activate tracker38
  pytest
  source deactivate

  pyenv activate tracker38redis
  pytest
  source deactivate

  pyenv activate tracker39
  pytest
  source deactivate

  pyenv activate tracker39redis
  pytest
  source deactivate

  pyenv activate tracker310
  pytest
  source deactivate

  pyenv activate tracker310redis
  pytest
  source deactivate

  pyenv activate tracker311
  pytest
  source deactivate

  pyenv activate tracker311redis
  pytest
  source deactivate

}

function refresh_deploy {
  pyenv uninstall -f tracker35
  pyenv uninstall -f tracker35redis
  pyenv uninstall -f tracker36
  pyenv uninstall -f tracker36redis
  pyenv uninstall -f tracker37
  pyenv uninstall -f tracker37redis
  pyenv uninstall -f tracker38
  pyenv uninstall -f tracker38redis
  pyenv uninstall -f tracker39
  pyenv uninstall -f tracker39redis
  pyenv uninstall -f tracker310
  pyenv uninstall -f tracker310redis
  pyenv uninstall -f tracker311
  pyenv uninstall -f tracker311redis
}


case "$1" in

  "deploy")  echo "Deploying python environments. This can take few minutes"
      deploy
      ;;
  "test")  echo "Running tests"
      run_tests
      ;;
  "refresh") echo "Refreshing python environments"
      refresh_deploy
      deploy
      ;;
  *) echo "Unknown subcommand. Specify deploy or test"
      exit 1
      ;;

esac
