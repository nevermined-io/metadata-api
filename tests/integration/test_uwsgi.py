"""Integration tests meant to be run with flask running under uwsgi"""
import time

import requests
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(reason='Arweave disabled')
def test_update_external_status_slow(dao, base_ddo_url, json_dict):
    r = requests.post(
        f'http://localhost:5000{base_ddo_url}',
        json=json_dict
    )

    # try to check status every minute for max 10 minutes
    retries = 10
    while retries > 0:
        r = requests.get(
            f'http://localhost:5000{base_ddo_url}/{json_dict["id"]}/status'
        )

        status = r.json()
        if status['external']['status'] == 'ACCEPTED':
            break

        retries -= 1
        time.sleep(60)
    else:
        raise TimeoutError

    # cleanup
    dao.metadatadb.delete(json_dict['id'])