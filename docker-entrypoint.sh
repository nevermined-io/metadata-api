#!/bin/sh

export CONFIG_FILE=/nevermind_metadata/config.ini
envsubst < /nevermind_metadata/config.ini.template > /nevermind_metadata/config.ini
gunicorn -b ${AQUARIUS_URL#*://} -w ${AQUARIUS_WORKERS} nevermind_metadata.run:app
tail -f /dev/null
