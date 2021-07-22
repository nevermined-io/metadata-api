import json

import pytest
pytestmark = pytest.mark.arweave


def test_create_ddo(client, base_ddo_url, json_dict, dao):
    """Test creation of asset"""
    rv = client.get(
        base_ddo_url + '/%s' % json_dict['id'],
        content_type='application/json')
    assert rv.status_code == 200

    status = dao._get_external_index(json_dict['id'])
    assert status['did'] == json_dict['id']
    assert len(status['externalId']) == 43
    assert status['type'] == 'Arweave'
    assert status['status'] == 'PENDING'


def test_update_ddo(client, base_ddo_url, json_dict, json_update):
    put = client.put(
        f'{base_ddo_url}/{json_dict["id"]}',
        data=json.dumps(json_update),
        content_type='application/json')
    assert put.status_code == 405


def test_delete_ddo(client, base_ddo_url, json_dict):
    delete = client.delete(f'{base_ddo_url}/{json_dict["id"]}')
    assert delete.status_code == 405