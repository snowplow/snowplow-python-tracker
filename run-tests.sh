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
    pyenv virtualenv 2.7.15 tracker27
    pyenv activate tracker27
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.4.9
  if [ ! -f ~/.pyenv/versions/tracker34 ]; then
    pyenv virtualenv 3.4.9 tracker34
    pyenv activate tracker34
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.5.2
  if [ ! -f ~/.pyenv/versions/tracker35 ]; then
    pyenv virtualenv 3.5.2 tracker35
    pyenv activate tracker35
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.7.1
  if [ ! -f ~/.pyenv/versions/tracker37 ]; then
    pyenv virtualenv 3.7.1 tracker37
    pyenv activate tracker37
    pip install .
    pip install -r requirements-test.txt
    source deactivate
  fi
}


function run_tests {
  pyenv activate tracker27
  pytest -s
  source deactivate
  
  pyenv activate tracker34
  pytest
  source deactivate
  
  pyenv activate tracker35
  pytest
  source deactivate

  pyenv activate tracker37
  pytest
  source deactivate 
}

function refresh_deploy {
  pyenv uninstall -f tracker27
  pyenv uninstall -f tracker34
  pyenv uninstall -f tracker35
  pyenv uninstall -f tracker37
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
