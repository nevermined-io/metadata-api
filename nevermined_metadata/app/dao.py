import logging

from metadatadb_driver_interface import MetadataDb
from metadatadb_driver_interface.search_model import FullTextModel, QueryModel


class Dao(object):

    def __init__(self, config_file=None):
        self.metadatadb = MetadataDb(config_file).plugin

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
        return self.metadatadb.write(record, asset_id)

    def update(self, record, asset_id):
        return self.metadatadb.update(record, asset_id)

    def delete(self, asset_id):
        return self.metadatadb.delete(asset_id)

    def query(self, query):
        query_list = []
        if isinstance(query, QueryModel):
            query_result, count = self.metadatadb.query(query)
        elif isinstance(query, FullTextModel):
            query_result, count = self.metadatadb.text_query(query)
        else:
            raise TypeError('Unrecognized `query` type %s' % type(query))

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
