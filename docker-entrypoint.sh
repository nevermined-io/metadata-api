#!/bin/sh

export CONFIG_FILE=/nevermined_metadata/config.ini
envsubst < /nevermined_metadata/config.ini.template > /nevermined_metadata/config.ini
#envsubst < /nevermined_metadata/uwsgi.ini.template > /nevermined_metadata/uwsgi.ini
uwsgi --ini uwsgi.ini.template
tail -f /dev/null