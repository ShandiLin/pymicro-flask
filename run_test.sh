#!/usr/bin/env bash

APP_HOME="$(cd "`dirname "$0"`"; pwd)"

if [ -z $PYMICRO_DATADIR ]
then
    echo "PYMICRO_DATADIR not set, using default: /tmp"
    export PYMICRO_DATADIR=/tmp/test
fi
export PYMICRO_CONFIG=$APP_HOME/test/test_data/conf/test_config.toml

# run python tests
pip install -r $APP_HOME/docs/requirements-test.txt
pytest --cov=pymicro_flask --cov-report term-missing
