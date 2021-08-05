import json

import pytest

from nevermined_metadata.constants import BaseURLs
from nevermined_metadata.run import create_app
from nevermined_metadata.app.dao import get_dao


@pytest.fixture(scope="session", autouse=True)
def app():
    app = create_app(config_file='./tests/resources/config-test-external.ini')
    with app.app_context():
        yield app


@pytest.fixture
def dao(app):
    return get_dao()


@pytest.fixture
def client(app, json_update, json_dict, dao):
    client = app.test_client()
    client.post(BaseURLs.BASE_METADATA_URL + '/assets/ddo',
                data=json.dumps(json_update),
                content_type='application/json')
    client.post(BaseURLs.BASE_METADATA_URL + '/assets/ddo',
                data=json.dumps(json_dict),
                content_type='application/json')

    yield client

    dao.metadatadb.delete(json_dict['id'])
    dao.metadatadb.delete(json_update['id'])