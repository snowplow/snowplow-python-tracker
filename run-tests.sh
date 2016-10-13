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

  # pyenv install 2.7.12
  if [ ! -f ~/.pyenv/versions/tracker27 ]; then
    pyenv virtualenv 2.7.12 tracker27
    pyenv activate tracker27
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.3.6
  if [ ! -f ~/.pyenv/versions/tracker33 ]; then
    pyenv virtualenv 3.3.6 tracker33
    pyenv activate tracker33
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.4.5
  if [ ! -f ~/.pyenv/versions/tracker34 ]; then
    pyenv virtualenv 3.4.5 tracker34
    pyenv activate tracker34
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    source deactivate
  fi

  # pyenv install 3.5.2
  if [ ! -f ~/.pyenv/versions/tracker35 ]; then
    pyenv virtualenv 3.5.2 tracker35
    pyenv activate tracker35
    pip install -r requirements.txt
    pip install -r requirements-test.txt
    source deactivate
  fi

}


function run_tests {
  
  pyenv activate tracker27
  pytest -s
  source deactivate
  
  pyenv activate tracker33
  pytest
  source deactivate
  
  pyenv activate tracker34
  pytest
  source deactivate
  
  pyenv activate tracker35
  pytest
  source deactivate 
}  


case "$1" in

  "deploy")  echo "Deploying python environments. This can take few minutes"
      deploy
      ;;
  "test")  echo  "Running tests"
      run_tests
      ;;
  *) echo "Unknown subcommand. Specify deploy or test"
      exit 1
      ;;

esac
