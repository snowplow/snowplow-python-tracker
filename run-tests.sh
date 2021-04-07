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
  # pyenv install 2.7.15
  if [ ! -f ~/.pyenv/versions/tracker27 ]; then
    pyenv virtualenv 2.7.18 tracker27
    pyenv activate tracker27
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -f ~/.pyenv/versions/tracker27redis ]; then
    pyenv virtualenv 2.7.18 tracker27redis
    pyenv activate tracker27redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.5.10
  if [ ! -f ~/.pyenv/versions/tracker35 ]; then
    pyenv virtualenv 3.5.10 tracker35
    pyenv activate tracker35
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -f ~/.pyenv/versions/tracker35redis ]; then
    pyenv virtualenv 3.5.10 tracker35redis
    pyenv activate tracker35redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.6.12
  if [ ! -f ~/.pyenv/versions/tracker36 ]; then
    pyenv virtualenv 3.6.12 tracker36
    pyenv activate tracker36
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -f ~/.pyenv/versions/tracker36redis ]; then
    pyenv virtualenv 3.6.12 tracker36redis
    pyenv activate tracker36redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.7.9
  if [ ! -f ~/.pyenv/versions/tracker37 ]; then
    pyenv virtualenv 3.7.9 tracker37
    pyenv activate tracker37
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -f ~/.pyenv/versions/tracker37redis ]; then
    pyenv virtualenv 3.7.9 tracker37redis
    pyenv activate tracker37redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.8.6
  if [ ! -f ~/.pyenv/versions/tracker38 ]; then
    pyenv virtualenv 3.8.6 tracker38
    pyenv activate tracker38
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -f ~/.pyenv/versions/tracker38redis ]; then
    pyenv virtualenv 3.8.6 tracker38redis
    pyenv activate tracker38redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.9.0
  if [ ! -f ~/.pyenv/versions/tracker39 ]; then
    pyenv virtualenv 3.9.0 tracker39
    pyenv activate tracker39
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  if [ ! -f ~/.pyenv/versions/tracker39redis ]; then
    pyenv virtualenv 3.9.0 tracker39redis
    pyenv activate tracker39redis
    pip install .[redis]
    pip install -r requirements-test.txt
    source deactivate
  fi
}


function run_tests {
  pyenv activate tracker27
  pytest -s
  source deactivate

  pyenv activate tracker27redis
  pytest -s
  source deactivate

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
}

function refresh_deploy {
  pyenv uninstall -f tracker27
  pyenv uninstall -f tracker27redis
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
