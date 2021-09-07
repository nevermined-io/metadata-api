#!/bin/sh

export CONFIG_PATH=/nevermined_metadata/config.ini
export CONFIG_FILE=/nevermined_metadata/config.ini
envsubst < /nevermined_metadata/config.ini.template > /nevermined_metadata/config.ini
# uwsgi --ini uwsgi.ini.template
gunicorn -b ${METADATA_URL#*://} -w ${METADATA_WORKERS} nevermined_metadata.run:app
tail -f /dev/null