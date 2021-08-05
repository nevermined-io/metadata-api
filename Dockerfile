FROM python:3.8-slim-buster
LABEL maintainer="Keyko <root@keyko.io>"

ARG VERSION

RUN apt -y update
RUN apt -y install build-essential gettext-base libpcre3 libpcre3-dev \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

COPY . /nevermined_metadata

RUN chown -R uwsgi:uwsgi /nevermined_metadata
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
ENV METADATA_HOST='0.0.0.0:5000'
ENV ALLOW_FREE_ASSETS_ONLY='false'
# docker-entrypoint.sh configuration file variables
ENV METADATA_WORKERS='4'

ENTRYPOINT ["/nevermined_metadata/docker-entrypoint.sh"]

EXPOSE 5000
