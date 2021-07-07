[![banner](https://raw.githubusercontent.com/nevermined-io/assets/main/images/logo/banner_logo.png)](https://nevermined.io)

# Nevermined Metadata API

> Nevermined metadata provides an off-chain database store for metadata about data assets.

![Nevermined metadata](https://github.com/nevermined-io/metadata-api/workflows/Python%20package/badge.svg)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/neverminedio/metadata-api.svg)](https://hub.docker.com/repository/docker/neverminedio/metadata-api)
[![GitHub contributors](https://img.shields.io/github/contributors/nevermined-io/metadata-api.svg)](https://github.com/nevermined-io/metadata-api/graphs/contributors)

## For Metadata Operators

If you're developing a marketplace, you'll want to run Nevermined Metadata and several other components locally, and the easiest way to do that is to use Nevermined tools. See the instructions in [Nevemind tools repository](https://github.com/nevermined-io/tools).

## For Metadata API Users

If you have Nevermined metadata running locally, you can find API documentation at
[http://localhost:5000/api/v1/docs](http://localhost:5000/api/v1/docs) or maybe
[http://0.0.0.0:5000/api/v1/docs](http://0.0.0.0:5000/api/v1/docs).

Tip 1: If that doesn't work, then try `https`.

Tip 2: If your browser shows the Swagger header across the top but says "Failed to load spec." then we found that, in Chrome, if we went to `chrome://flags/#allow-insecure-localhost` and toggled it to Enabled, then relaunched Chrome, it worked.

If you want to know more about the ontology of the metadata, you can find all the information in
[Metadata Ontology](https://github.com/nevermined-io/internal/tree/master/docs/architecture/specs/metadata).

## For Metadata Developers

### General Keyko Dev Docs

For information about Keyko's Python code style and related "meta" developer docs, see [Keyko Nevermined Internal](https://github.com/nevermined-io/internal).

### Running Locally, for Dev and Test

First, clone this repository:

```bash
git clone git@github.com:nevermined-io/metadata-api.git
cd metadata-api/
```

Then run mongodb database that is a requirement for Nevermined Metadata. MongoDB can be installed directly using instructions from [official documentation](https://docs.mongodb.com/manual/installation/). Or if you have `docker` installed, you can run:

```bash
docker run -d -p 27017:27017 mongo
```

Note that it runs MongoDB but the Nevermined Metadata can also work with Elasticsearch. If you want to run ElasticSearch, update the file `config.ini` and run the Database engine with your preferred method.

Then install Nevermined Metadata's OS-level requirements:

```bash
sudo apt update
sudo apt install python3-dev python3.7-dev libssl-dev
```

(Note: At the time of writing, `python3-dev` was for Python 3.6. `python3.7-dev` is needed if you want to test against Python 3.7 locally.)

Before installing Nevermined Metadatas's Python package requirements, you should create and activate a virtualenv (or equivalent).

The most simple way to start is:

```bash
pip install -r requirements.txt
export FLASK_APP=nevermined_metadata/run.py
export CONFIG_FILE=config.ini
flask run
```

That will use HTTP (i.e. not SSL/TLS).

The proper way to run the Flask application is using an application server such as Gunicorn. This allow you to run using SSL/TLS.
You can generate some certificates for testing by doing:

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

and when it asks for the Common Name (CN), answer `localhost`

Then edit the config file `config.ini` so that:

```yaml
metadata.url = http://localhost:5000
```

Then execute this command:

```bash
gunicorn --certfile cert.pem --keyfile key.pem -b 0.0.0.0:5000 -w 1 nevermined_metadata.run:app
```

### Configuration

You can pass the configuration using the CONFIG_FILE environment variable (recommended) or locating your configuration in config.ini file.

In the configuration there are now two sections:

- metadatadb: Contains different values to connect with metadatadb. You can find more information about how to use MetadataDB [here](https://github.com/nevermined-io/metadata-driver-interface).
- resources: In this section we are showing the url in which the nevermined metadata is going to be deployed.

```yaml
[resources]
metadata.url = http://localhost:5000
```

### Testing

Automatic tests are set up via Github actions.
Our tests use the pytest framework.

### New Version

The `bumpversion.sh` script helps bump the project version. You can execute the script using `{major|minor|patch}` as first argument, to bump the version accordingly.

## Attribution

This project is based in the [Ocean Protocol Aquarius](https://github.com/oceanprotocol/aquarius). It keeps the same Apache v2 License and adds some improvements.
See [NOTICE file](NOTICE).

## License
```
Copyright 2020 Keyko GmbH
This product includes software developed at
BigchainDB GmbH and Ocean Protocol (https://www.oceanprotocol.com/)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
