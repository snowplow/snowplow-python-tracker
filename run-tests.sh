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

  # pyenv install 3.6.15
  if [ ! -e ~/.pyenv/versions/tracker36 ]; then
    pyenv virtualenv 3.6.15 tracker36
    pyenv activate tracker36
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.7.17
  if [ ! -e ~/.pyenv/versions/tracker37 ]; then
    pyenv virtualenv 3.7.17 tracker37
    pyenv activate tracker37
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.8.20
  if [ ! -e ~/.pyenv/versions/tracker38 ]; then
    pyenv virtualenv 3.8.20 tracker38
    pyenv activate tracker38
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.9.20
  if [ ! -e ~/.pyenv/versions/tracker39 ]; then
    pyenv virtualenv 3.9.20 tracker39
    pyenv activate tracker39
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.10.15
  if [ ! -e ~/.pyenv/versions/tracker310 ]; then
    pyenv virtualenv 3.10.15 tracker310
    pyenv activate tracker310
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.11.10
  if [ ! -e ~/.pyenv/versions/tracker311 ]; then
    pyenv virtualenv 3.11.10 tracker311
    pyenv activate tracker311
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.12.7
  if [ ! -e ~/.pyenv/versions/tracker312 ]; then
    pyenv virtualenv 3.12.7 tracker312
    pyenv activate tracker312
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.13.0
  if [ ! -e ~/.pyenv/versions/tracker313 ]; then
    pyenv virtualenv 3.13.0 tracker313
    pyenv activate tracker313
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi
}


function run_tests {
  pyenv activate tracker35
  pytest
  source deactivate

  pyenv activate tracker36
  pytest
  source deactivate

  pyenv activate tracker37
  pytest
  source deactivate

  pyenv activate tracker38
  pytest
  source deactivate

  pyenv activate tracker39
  pytest
  source deactivate

  pyenv activate tracker310
  pytest
  source deactivate

  pyenv activate tracker311
  pytest
  source deactivate

  pyenv activate tracker312
  pytest
  source deactivate

  pyenv activate tracker313
  pytest
  source deactivate
}

function refresh_deploy {
  pyenv uninstall -f tracker35
  pyenv uninstall -f tracker36
  pyenv uninstall -f tracker37
  pyenv uninstall -f tracker38
  pyenv uninstall -f tracker39
  pyenv uninstall -f tracker310
  pyenv uninstall -f tracker311
  pyenv uninstall -f tracker312
  pyenv uninstall -f tracker313
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
