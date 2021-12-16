import copy
import logging
import configparser

from flask import current_app, g, url_for

from metadatadb_driver_interface import MetadataDb
from metadatadb_driver_interface.search_model import FullTextModel, QueryModel
from metadatadb_driver_interface.constants import CONFIG_OPTION_EXTERNAL
from nevermined_metadata.constants import ConfigSections

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
        self._agreements_index = ConfigSections.AGREEMENTS
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
        external_id = None
        external_status = None
        if self.metadatadb_external is not None:
            external_id = self.metadatadb_external.write(
                self._datetime_to_date(record))
            external_status = 'PENDING'
            logger.info('Submitted %s to %s with id %s', asset_id,
                self.metadatadb_external.type, external_id)

        internal_id = self.metadatadb.write(record, asset_id)
        internal_url = url_for('assets.get_ddo', did=internal_id, _external=True)
        self._update_status_index(asset_id, internal_id, 'ACCEPTED', external_id, external_status, internal_url)

        return internal_id

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

    def status(self, asset_id):
        return self._get_status_index(asset_id)

    @staticmethod
    def is_listed(services):
        for service in services:
            if service['type'] == 'metadata':
                if 'curation' in service['attributes'] and 'isListed' in service['attributes']['curation']:
                    return service['attributes']['curation']['isListed']

    def update_external_status(self):
        results = self._es.search(
            index=self._external_index,
            body={
                'query': {
                    'match': {
                        'external.status': {
                            'query': 'PENDING'
                        }
                    },
                }
            },
            filter_path=['hits.hits._source']
        )

        if 'hits' not in results:
            return

        for result in results['hits']['hits']:
            document = result['_source']
            new_status = self.metadatadb_external.status(document['external']['id'])
            logger.info("%s: %s", document['external']['id'], new_status)
            self._update_status_index(
                document['did'],
                document['internal']['id'],
                document['internal']['status'],
                document['external']['id'],
                new_status
            )

    def _update_status_index(self, did, internal_id, internal_status, external_id, external_status, internal_url=None):
        body = {
            'did': did,
            'internal': {
                'id': internal_id,
                'type': self.metadatadb.type,
                'status': internal_status,
                'url': internal_url
            },
            'external': None
        }

        if external_id is not None:
            # TODO: Add a url method to the driver interface
            external_url = f'{self.metadatadb_external.driver.wallet.api_url}/{external_id}'
            body.update({
                    'external': {
                        'id': external_id,
                        'type': self.metadatadb_external.type,
                        'status': external_status,
                        'url': external_url

                    }
                }
            )
        logger.info('Updating external index %s', body)
        return self._es.index(
            index=self._external_index,
            id=did,
            body=body,
            refresh='wait_for'
        )['_id']

    def _get_status_index(self, did):
        return self._es.get(
            index = self._external_index,
            id=did
        )['_source']

    def persist_service_agreement(self, agreementId, body):
        return self._es.index(
            index=self._agreements_index,
            id=agreementId,
            body=body,
            refresh='wait_for'
        )['agreement']

    def get_service_agreement(self, agreementId):
        return self._es.get(
            index=self._agreements_index,
            id=agreementId,
        )['agreement']

    def _init_elasticsearch(self):
        mapping = {
            'mappings': {
                'properties': {
                    'did': {
                        'type': 'text'
                    },
                    'internal': {
                        'properties': {
                            'id': {
                                'type': 'text'
                            },
                            'type': {
                                'type': 'text'
                            },
                            'status': {
                                'type': 'text'
                            },
                            'url': {
                                'type': 'text'
                            }
                        }
                    },
                    'external': {
                        'properties': {
                            'id': {
                                'type': 'text'
                            },
                            'type': {
                                'type': 'text'
                            },
                            'status': {
                                'type': 'text'
                            },
                            'url': {
                                'type': 'text'
                            }
                        }
                    }
                }
            }
        }

        serviceMapping = {
            'mappings': {
                'agreement': {
                    'dynamic': 'true',
                }
            }
        }

        logger.info('Initializing elasticsearch...')
        result = self._es.indices.create(index=self._external_index, ignore=400, body=mapping)
        logger.info(result)
        resultAgreement = self._es.indices.create(index=self._agreements_index, ignore=400, body=serviceMapping)
        logger.info(resultAgreement)


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