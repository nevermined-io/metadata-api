#!/bin/sh

export CONFIG_FILE=/nevermined_metadata/config.ini
envsubst < /nevermined_metadata/config.ini.template > /nevermined_metadata/config.ini
gunicorn -b ${METADATA_URL#*://} -w ${METADATA_WORKERS} nevermined_metadata.run:app
tail -f /dev/null
