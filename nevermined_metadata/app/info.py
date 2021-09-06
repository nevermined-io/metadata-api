import configparser

from elasticsearch import Elasticsearch
from pymongo.mongo_client import MongoClient
from flask.blueprints import Blueprint
from flask import current_app, url_for
from flask.json import jsonify
from flask_swagger import swagger

from nevermined_metadata.constants import Metadata
from nevermined_metadata.config import Config


info = Blueprint('info', __name__)

@info.route("/")
def version():
    config = Config(current_app.config['CONFIG_FILE'])
    info = {
        'software': Metadata.TITLE,
        'version': get_version(),
        'plugins': [config.module]
    }

    if config.module_external is not None:
        info['plugins'].append(config.module_external)

    return jsonify(info)


@info.route("/health")
def health():
    config = Config(current_app.config['CONFIG_FILE'])
    return get_status(config)


@info.route("/spec")
def spec():
    config = Config(current_app.config['CONFIG_FILE'])
    template = {
        'info': {
            'version': get_version(),
            'title': Metadata.TITLE,
            'description': f'{Metadata.DESCRIPTION}`{config.metadata_url}`.',
            'connected': get_status(config)
        }
    }
    swag = swagger(current_app, from_file_keyword='swagger_from_file', template=template)
    return jsonify(swag)


def get_version():
    conf = configparser.ConfigParser()
    conf.read('.bumpversion.cfg')
    return conf['bumpversion']['current_version']


# TODO: Move this code to the drivers
def get_status(config):
    if config.get('metadatadb', 'module') == 'elasticsearch':
        if Elasticsearch(config.db_url).ping():
            return 'Elasticsearch connected', 200
        else:
            return 'Not connected to any database', 400
    elif config.get('metadatadb', 'module') == 'mongodb':
        if MongoClient(config.db_url).get_database(config.get('metadatadb', 'db.name')).command(
                'ping'):
            return 'Mongodb connected', 200
        else:
            return 'Not connected to any database', 400
    else:
        return 'Not connected to any database', 400