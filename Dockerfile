FROM python:3.6-alpine
LABEL maintainer="Keyko <root@keyko.io>"

ARG VERSION

RUN apk add --no-cache --update\
    build-base \
    gcc \
    gettext\
    gmp \
    gmp-dev \
    libffi-dev \
    openssl-dev \
    py-pip \
    python3 \
    python3-dev \
  && pip install virtualenv

COPY . /nevermined_metadata
WORKDIR /nevermined_metadata

# Only install install_requirements, not dev_ or test_requirements
RUN pip install .

# config.ini configuration file variables
ENV DB_MODULE='mongodb'
ENV DB_HOSTNAME='localhost'
ENV DB_PORT='27017'
#MONGO
ENV DB_NAME='nevermined_metadata'
ENV DB_COLLECTION='ddo'
#ELASTIC
ENV DB_INDEX='nevermined_metadata'
#BDB
ENV DB_SECRET=''
ENV DB_SCHEME='http'
ENV DB_NAMESPACE='namespace'
ENV METADATA_URL='http://0.0.0.0:5000'
ENV ALLOW_FREE_ASSETS_ONLY='false'
# docker-entrypoint.sh configuration file variables
ENV METADATA_WORKERS='1'

ENTRYPOINT ["/nevermined_metadata/docker-entrypoint.sh"]

EXPOSE 5000
