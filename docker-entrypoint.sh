#!/bin/sh

export CONFIG_PATH=/nevermined_metadata/config.ini
export CONFIG_FILE=/nevermined_metadata/config.ini
envsubst < /nevermined_metadata/config.ini.template > /nevermined_metadata/config.ini
uwsgi --ini uwsgi.ini.template
tail -f /dev/null