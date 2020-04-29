#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import copy
import json
from urllib.request import urlopen

import pytest

from nevermined_metadata.constants import BaseURLs
from nevermined_metadata.run import app

app = app


@pytest.fixture
def base_ddo_url():
    return BaseURLs.BASE_METADATA_URL + '/assets/ddo'


@pytest.fixture
def client_with_no_data():
    client = app.test_client()
    yield client


@pytest.fixture
def client():
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


json_dict = json.loads(urlopen(
    "https://raw.githubusercontent.com/keyko-io/nevermined-docs/master/architecture/specs/examples/access/v0.1/ddo1.json").read().decode('utf-8'))

json_dict2 = json.loads(urlopen(
    "https://raw.githubusercontent.com/keyko-io/nevermined-docs/master/architecture/specs/examples/access/v0.1/ddo1-upsert.json").read().decode('utf-8'))
json_dict_no_metadata = {"publisherId": "0x2"}
json_dict_no_valid_metadata = {"publisherId": "0x4",
                               "main": {},
                               "assetId": "002"
                               }

json_before = json.loads(urlopen(
    "https://raw.githubusercontent.com/keyko-io/nevermined-docs/master/architecture/specs/examples/access/v0.1/ddo2.json").read().decode('utf-8'))
json_update = json.loads(urlopen(
    "https://raw.githubusercontent.com/keyko-io/nevermined-docs/master/architecture/specs/examples/access/v0.1/ddo2-update.json").read().decode('utf-8'))

json_valid = json.loads(urlopen(
    "https://raw.githubusercontent.com/keyko-io/nevermined-docs/master/architecture/specs/examples/metadata/v0.1/metadata1.json").read().decode('utf-8'))

test_assets = []
for i in range(10):
    a = copy.deepcopy(json_dict)
    a['id'] = a['id'][:-2] + str(i) + str(i)
    test_assets.append(a)

json_request_consume = {
    'requestId': "",
    'consumerId': "",
    'fixed_msg': "",
    'sigEncJWT': ""
}
