#!/usr/bin/env bash

BASEDIR="$(cd "`dirname "$0"`"; pwd)"

# build and install python libraries
python $BASEDIR/setup.py bdist_wheel
cd ../
pip install --upgrade --force-reinstall $BASEDIR/dist/*.whl
python $BASEDIR/setup.py clean

# check if pymicro_server executable exists
PYMICRO_EXECUTABLE=$(dirname $(dirname $(which pymicro_server)))
if [ -z $PYMICRO_EXECUTABLE ]
then
    echo "pymicro_server executable not found, check if python install correctly"
    exit 1
fi

# Install uwsgi plugins: https://github.com/DataDog/uwsgi-dogstatsd
if [ -z $PYMICRO_UWSGI_PLUGIN_DIR ]
then
    echo "set PYMICRO_UWSGI_PLUGIN_DIR to '/usr/local/lib/uwsgi_plugins' to hold plugins"
    export PYMICRO_UWSGI_PLUGIN_DIR=/usr/local/lib/uwsgi_plugins
fi
mkdir -p $PYMICRO_UWSGI_PLUGIN_DIR
cd $PYMICRO_UWSGI_PLUGIN_DIR
uwsgi --build-plugin https://github.com/Datadog/uwsgi-dogstatsd
rm -rf $PYMICRO_UWSGI_PLUGIN_DIR/uwsgi-dogstatsd
