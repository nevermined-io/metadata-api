import copy
from datetime import datetime
import logging
import configparser

from flask import current_app, g

from metadatadb_driver_interface import MetadataDb, metadatadb
from metadatadb_driver_interface.search_model import FullTextModel, QueryModel
from metadatadb_driver_interface.constants import CONFIG_OPTION_EXTERNAL

logger = logging.getLogger(__name__)


class Dao(object):

    def __init__(self, config_file=None):
        self.metadatadb = MetadataDb(config_file).plugin
        self.metadatadb_external = None

        try:
            self.metadatadb_external = MetadataDb(config_file, config_option=CONFIG_OPTION_EXTERNAL).plugin
        except configparser.NoSectionError:
            logger.info('No external plugin found.')

        self._es = self.metadatadb.driver._es
        self._external_index = CONFIG_OPTION_EXTERNAL
        self._init_elasticsearch()


    def get_all_listed_assets(self):
        assets = self.metadatadb.list()
        asset_with_id = []
        for asset in assets:
            try:
                if self.is_listed(asset['service']):
                    asset_with_id.append(self.metadatadb.read(asset['id']))
            except Exception as e:
                logging.error(str(e))
                pass
        return asset_with_id

    def get_all_assets(self):
        assets = self.metadatadb.list()
        asset_with_id = []
        for asset in assets:
            try:
                asset_with_id.append(self.metadatadb.read(asset['id']))
            except Exception as e:
                logging.error(str(e))
                pass
        return asset_with_id

    def get(self, asset_id):
        try:
            asset = self.metadatadb.read(asset_id)
        except Exception as e:
            logging.error(str(e))
            asset = None

        if asset is None:
            return asset
        elif self.is_listed(asset['service']):
            return asset
        else:
            return None

    def register(self, record, asset_id):
        if self.metadatadb_external is not None:
            transaction_id = self.metadatadb_external.write(
                self._datetime_to_date(record))
            self._update_external_index(asset_id, transaction_id, 'PENDING')
            logger.info('Submitted %s to %s with txid %s', asset_id,
                self.metadatadb_external.type, transaction_id)

        return self.metadatadb.write(record, asset_id)

    def update(self, record, asset_id):
        if self.metadatadb_external is not None:
            self.metadatadb_external.update(record, asset_id)
            logger.info('Updating asset %s', asset_id)
        return self.metadatadb.update(record, asset_id)

    def delete(self, asset_id):
        if self.metadatadb_external is not None:
            self.metadatadb_external.delete(asset_id)
            logger.info('Deleting asset %s', asset_id)
        return self.metadatadb.delete(asset_id)

    def query(self, query, show_unlisted=False):
        query_list = []
        if isinstance(query, QueryModel):
            query_result, count = self.metadatadb.query(query)
        elif isinstance(query, FullTextModel):
            query_result, count = self.metadatadb.text_query(query)
        else:
            raise TypeError('Unrecognized `query` type %s' % type(query))
        if show_unlisted:
            return query_result, count
        else:
            for f in query_result:
                if self.is_listed(f['service']):
                    query_list.append(f)

            return query_list, count

    @staticmethod
    def is_listed(services):
        for service in services:
            if service['type'] == 'metadata':
                if 'curation' in service['attributes'] and 'isListed' in service['attributes']['curation']:
                    return service['attributes']['curation']['isListed']

    def _update_external_index(self, did, external_id, status):
        body = {
            'did': did,
            'externalId': external_id,
            'type': self.metadatadb_external.type,
            'status': status,
        }
        logger.info('Updating external index %s', body)
        return self._es.index(
            index=self._external_index,
            id=did,
            body=body,
            refresh='wait_for'
        )['_id']

    def _get_external_index(self, did):
        return self._es.get(
            index = self._external_index,
            id=did
        )['_source']

    def _init_elasticsearch(self):
        mapping = {
            'mappings': {
                'members': {
                    'properties': {
                        'did': {
                            'type': 'text'
                        },
                        'externalId': {
                            'type': 'text'
                        },
                        'type': {
                            'type': 'text'
                        },
                        'status': {
                            'type': 'text'
                        }
                    }
                }
            }
        }

        logger.info('Initializing elasticsearch...')
        self._es.indices.create(index=self._external_index, ignore=400, body=mapping)

    @staticmethod
    def _datetime_to_date(record):
        result = copy.deepcopy(record)
        result['created'] = result['created'].strftime('%Y-%m-%dT%H:%M:%SZ')


        for i, service in enumerate(result['service']):
            if service['type'] == 'metadata':
                result['service'][i]['attributes']['main']['dateCreated'] = \
                    result['service'][i]['attributes']['main']['dateCreated'] \
                        .strftime('%Y-%m-%dT%H:%M:%SZ')

        return result



def get_dao():
    if 'dao' not in g:
        g.dao = Dao(config_file=current_app.config['CONFIG_FILE'])

    return g.dao