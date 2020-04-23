#!/bin/sh

export CONFIG_FILE=/nevermind_metadata/config.ini
envsubst < /nevermind_metadata/config.ini.template > /nevermind_metadata/config.ini
gunicorn -b ${METADATA_URL#*://} -w ${METADATA_WORKERS} nevermind_metadata.run:app
tail -f /dev/null
