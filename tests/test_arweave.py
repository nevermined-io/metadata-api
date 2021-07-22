import json
from nevermined_metadata.config import Config

from nevermined_metadata.app.assets import validate_date_format
from nevermined_metadata.constants import BaseURLs
from nevermined_metadata.app.dao import get_dao
from tests.conftest import (json_before, json_dict, json_dict2, json_dict_no_metadata,
                            json_dict_no_valid_metadata, json_update, json_valid, test_assets)


def test_create_ddo(client, base_ddo_url):
    """Test creation of asset"""
    rv = client.get(
        base_ddo_url + '/%s' % json_dict['id'],
        content_type='application/json')
    assert rv.status_code == 200

    status = get_dao()._get_external_index(json_dict['id'])
    assert status['did'] == json_dict['id']
    assert len(status['externalId']) == 43
    assert status['type'] == 'Arweave'
    assert status['status'] == 'PENDING'


def test_update_ddo(client, base_ddo_url):
    put = client.put(
        f'{base_ddo_url}/{json_dict["id"]}',
        data=json.dumps(json_update),
        content_type='application/json')
    assert put.status_code == 405


def test_delete_ddo(client, base_ddo_url):
    delete = client.delete(f'{base_ddo_url}/{json_dict["id"]}')
    assert delete.status_code == 405