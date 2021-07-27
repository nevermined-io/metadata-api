import json

import pytest

pytestmark = pytest.mark.arweave


def test_create_ddo(client, base_ddo_url, json_dict, dao):
    """Test creation of asset"""
    rv = client.get(
        base_ddo_url + '/%s' % json_dict['id'],
        content_type='application/json')
    assert rv.status_code == 200

    status = dao._get_status_index(json_dict['id'])
    status_external = status['external']
    expected_url = f'{dao.metadatadb_external.driver.wallet.api_url}/tx/{status_external["id"]}'

    assert status['did'] == json_dict['id']
    assert status_external is not None
    assert status_external['id'] is not None
    assert status_external['type'] == 'Arweave'
    assert status_external['status'] == 'PENDING'
    assert status_external['url'] == expected_url


def test_update_ddo(client, base_ddo_url, json_dict, json_update):
    put = client.put(
        f'{base_ddo_url}/{json_dict["id"]}',
        data=json.dumps(json_update),
        content_type='application/json')
    assert put.status_code == 405


def test_delete_ddo(client, base_ddo_url, json_dict):
    delete = client.delete(f'{base_ddo_url}/{json_dict["id"]}')
    assert delete.status_code == 405