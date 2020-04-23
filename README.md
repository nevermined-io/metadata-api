[![banner](https://raw.githubusercontent.com/keyko-io/assets/master/images/logo/small/keyko_logo@2x-100.jpg)](https://keyko.io)

# nevermind-metadata

> Nevermind metadata provides an off-chain database store for metadata about data assets.

[![Docker Build Status](https://img.shields.io/docker/build/keykoio/nevermind-metadata.svg)](https://hub.docker.com/r/keykoio/nevermind-metadata/) 
![Nevermind metadata](https://github.com/keyko-io/nevermind-metadata/workflows/Python%20package/badge.svg)
[![GitHub contributors](https://img.shields.io/github/contributors/keyko-io/nevermind-metadata.svg)](https://github.com/keyko-io/nevermind-metadata/graphs/contributors)

## For Aquarius Operators

If you're developing a marketplace, you'll want to run Nevermind Metadata and several other components locally, and the easiest way to do that is to use Nevermind tools. See the instructions in [Nevemind tools repository](https://github.com/keyko-io/nevermind-tools).

## For Aquarius API Users

The Ocean Protocol docs site has [documentation about the Aquarius API](https://docs.oceanprotocol.com/references/aquarius/). Note that it shows the docs for the version currently deployed with the Nile Testnet. To get documentation for other versions, there is a "past versions" link at the top of the page.

If you have Nevermind metadata running locally, you can find API documentation at
[http://localhost:5000/api/v1/docs](http://localhost:5000/api/v1/docs) or maybe
[http://0.0.0.0:5000/api/v1/docs](http://0.0.0.0:5000/api/v1/docs).

Tip 1: If that doesn't work, then try `https`.

Tip 2: If your browser shows the Swagger header across the top but says "Failed to load spec." then we found that, in Chrome, if we went to `chrome://flags/#allow-insecure-localhost` and toggled it to Enabled, then relaunched Chrome, it worked.

If you want to know more about the ontology of the metadata, you can find all the information in
[Metadata Ontology](https://github.com/keyko-io/nevermind-internal/tree/master/docs/architecture/specs/metadata).

## For Aquarius Developers

### General Ocean Dev Docs

For information about Keyko's Python code style and related "meta" developer docs, see [Keyko Nevermind Internal](https://github.com/keyko-io/nevermind-internal).

### Running Locally, for Dev and Test

First, clone this repository:

```bash
git clone git@github.com:keyko-io/nevermind-metadata.git
cd nevermind-metadata/
```

Then run mongodb database that is a requirement for Aquarius. MongoDB can be installed directly using instructions from [official documentation](https://docs.mongodb.com/manual/installation/). Or if you have `docker` installed, you can run:

```bash
docker run -d -p 27017:27017 mongo
```

Note that it runs MongoDB but the Nevermind Metadata can also work with Elasticsearch. If you want to run ElasticSearch, update the file `config.ini` and run the Database engine with your preferred method.

Then install Neverminds Metadata's OS-level requirements:

```bash
sudo apt update
sudo apt install python3-dev python3.7-dev libssl-dev
```

(Note: At the time of writing, `python3-dev` was for Python 3.6. `python3.7-dev` is needed if you want to test against Python 3.7 locally.)

Before installing Nevermind Metadatas's Python package requirements, you should create and activate a virtualenv (or equivalent).

The most simple way to start is:

```bash
pip install -r requirements.txt
export FLASK_APP=nevermind_metadata/run.py
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
gunicorn --certfile cert.pem --keyfile key.pem -b 0.0.0.0:5000 -w 1 nevermind_metadata.run:app
```

### Configuration

You can pass the configuration using the CONFIG_FILE environment variable (recommended) or locating your configuration in config.ini file.

In the configuration there are now two sections:

- oceandb: Contains different values to connect with oceandb. You can find more information about how to use OceanDB [here](https://github.com/oceanprotocol/oceandb-driver-interface).
- resources: In this section we are showing the url in which the nevermind metadata is going to be deployed.

```yaml
[resources]
metadata.url = http://localhost:5000
```

### Testing

Automatic tests are set up via Github actions.
Our tests use the pytest framework.

### New Version

The `bumpversion.sh` script helps bump the project version. You can execute the script using `{major|minor|patch}` as first argument, to bump the version accordingly.

##Attribution
This project is based in the [Ocean Protocol Aquarius](https://github.com/oceanprotocol/aquarius). It keeps the same Apache v2 License and adds some improvements.

## License
```
Copyright 2020 Keyko GmbH.

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
