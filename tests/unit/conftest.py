import json

import pytest

from nevermined_metadata.constants import BaseURLs
from nevermined_metadata.run import create_app


@pytest.fixture(scope="session", autouse=True)
def app():
    app = create_app(config_file='./tests/resources/config-test.ini')
    with app.app_context():
        yield app

@pytest.fixture
def client_with_no_data(app):
    client = app.test_client()
    yield client


@pytest.fixture
def client(app, json_update, json_dict):
    client = app.test_client()
    client.delete(BaseURLs.BASE_METADATA_URL + '/assets/ddo')
    post = client.post(BaseURLs.BASE_METADATA_URL + '/assets/ddo',
                       data=json.dumps(json_update),
                       content_type='application/json')
    post2 = client.post(BaseURLs.BASE_METADATA_URL + '/assets/ddo',
                        data=json.dumps(json_dict),
                        content_type='application/json')

    yield client

    client.delete(
        BaseURLs.BASE_METADATA_URL + '/assets/ddo/%s' % json.loads(post.data.decode('utf-8'))['id'])
    client.delete(
        BaseURLs.BASE_METADATA_URL + '/assets/ddo/%s' % json.loads(post2.data.decode('utf-8'))[
            'id'])