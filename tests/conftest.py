import copy
import json
from urllib.request import urlopen

import pytest

from nevermined_metadata.constants import BaseURLs


@pytest.fixture
def base_ddo_url():
    return BaseURLs.BASE_METADATA_URL + '/assets/ddo'

@pytest.fixture
def base_service_url():
    return BaseURLs.BASE_METADATA_URL + '/assets/service'

@pytest.fixture
def json_service():
    return {"agreementId": '0x00edffc52926739E8403E451b791378349f38818',"type":"nft-sales","index":6,"serviceEndpoint":"https://gateway.rinkeby.nevermined.rocks/api/v1/gateway/services/nft","did":"did:nv:249218ab779e6a16cd3ea1c630e7d97531343a1271cd5c16921e2491a65248c9","templateId":"0x24edffc52926739E8403E451b791378349f38818","attributes":{"main":{"name":"nftSalesAgreement","creator":"0xD0064bD1a8DD5a3F775A5432f833EaC9f21CcA80","datePublished":"2021-11-23T10:27:07Z","timeout":86400},"additionalInformation":{"description":""},"serviceAgreementTemplate":{"contractName":"NFTSalesTemplate","events":[{"name":"AgreementCreated","actorType":"consumer","handler":{"moduleName":"nftSalesTemplate","functionName":"fulfillLockPaymentCondition","version":"0.1"}}],"fulfillmentOrder":["lockPayment.fulfill","transferNFT.fulfill","escrowPayment.fulfill"],"conditionDependency":{"lockPayment":[],"transferNFT":[],"escrowPayment":["lockPayment","transferNFT"]},"conditions":[{"name":"lockPayment","timelock":0,"timeout":0,"contractName":"LockPaymentCondition","functionName":"fulfill","parameters":[{"name":"_did","type":"bytes32","value":"688190baee42efb665fb45799135f1511256839e84ccfa7b48616839c49fd427"},{"name":"_rewardAddress","type":"address","value":"0xD0064bD1a8DD5a3F775A5432f833EaC9f21CcA80"},{"name":"_tokenAddress","type":"address","value":"0x937Cc2ec24871eA547F79BE8b47cd88C0958Cc4D"},{"name":"_amounts","type":"uint256[]","value":["20"]},{"name":"_receivers","type":"address[]","value":["0xD0064bD1a8DD5a3F775A5432f833EaC9f21CcA80"]}]}]}}}

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
