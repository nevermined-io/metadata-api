import copy
import json
from urllib.request import urlopen

import pytest

from nevermined_metadata.constants import BaseURLs


@pytest.fixture
def base_ddo_url():
    return BaseURLs.BASE_METADATA_URL + '/assets/ddo'


@pytest.fixture
def json_dict():
    return json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs/examples/access/v0.1/ddo1.json").read().decode('utf-8'))


@pytest.fixture
def json_dict2():
    return json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs/examples/access/v0.1/ddo1-upsert.json").read().decode('utf-8'))


@pytest.fixture
def json_dict_no_metadata():
    return {"publisherId": "0x2"}


@pytest.fixture
def json_dict_no_valid_metadata():
    return {
        "publisherId": "0x4",
        "main": {},
        "assetId": "002"
    }


@pytest.fixture
def json_before():
    return json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs/examples/access/v0.1/ddo2.json").read().decode('utf-8'))


@pytest.fixture
def json_update():
    return json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs/examples/access/v0.1/ddo2-update.json").read().decode('utf-8'))


@pytest.fixture
def json_valid():
    return json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs/examples/metadata/v0.1/metadata1.json").read().decode('utf-8'))


@pytest.fixture
def test_assets(json_dict):
    result = []
    for i in range(10):
        a = copy.deepcopy(json_dict)
        a['id'] = a['id'][:-2] + str(i) + str(i)
        result.append(a)

    return result
