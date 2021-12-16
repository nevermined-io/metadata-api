import json

from flask import url_for

from nevermined_metadata.config import Config
from nevermined_metadata.app.assets import validate_date_format
from nevermined_metadata.constants import BaseURLs
from nevermined_metadata.app.info import get_status, get_version


def test_version(client):
    """Test version in root endpoint"""
    rv = client.get('/')

    assert json.loads(rv.data.decode('utf-8'))['software'] == 'Nevermined metadata'
    assert json.loads(rv.data.decode('utf-8'))['version'] == get_version()


def test_health(client, app):
    """Test health check endpoint"""
    config = Config(app.config['CONFIG_FILE'])
    rv = client.get('/health')

    assert rv.data.decode('utf-8') == get_status(config)[0]


def test_create_ddo(client, base_ddo_url, json_dict):
    """Test creation of asset"""
    rv = client.get(
        base_ddo_url + '/%s' % json_dict['id'],
        content_type='application/json')
    assert json_dict['id'] in json.loads(rv.data.decode('utf-8'))['id']
    assert json_dict['@context'] in json.loads(rv.data.decode('utf-8'))['@context']
    assert json_dict['service'][0]['type'] in json.loads(rv.data.decode('utf-8'))['service'][0][
        'type']


def test_status(client, base_ddo_url, json_dict, app):
    url = f'{base_ddo_url}/{json_dict["id"]}/status'
    response = client.get(url, content_type='application/json')
    assert response.status_code == 200

    status = response.get_json()
    with app.test_request_context():
        expected_url = url_for('assets.get_ddo', did=json_dict['id'], _external=True)

    assert status['did'] == json_dict['id']
    assert status['internal'] is not None
    assert status['internal']['id'] is not None
    assert status['internal']['type'] == 'Elasticsearch'
    assert status['internal']['status'] == 'ACCEPTED'
    assert status['internal']['url'] == expected_url


def test_post_with_no_ddo(client, base_ddo_url, json_dict_no_metadata):
    post = client.post(base_ddo_url,
                       data=json.dumps(json_dict_no_metadata),
                       content_type='application/json')
    assert 400 == post.status_code


def test_post_with_no_valid_ddo(client, base_ddo_url, json_dict_no_valid_metadata):
    post = client.post(base_ddo_url,
                       data=json.dumps(json_dict_no_valid_metadata),
                       content_type='application/json')
    assert 400 == post.status_code


def test_update_ddo(client_with_no_data, base_ddo_url, json_before, json_update):
    client = client_with_no_data
    post = client.post(base_ddo_url,
                       data=json.dumps(json_before),
                       content_type='application/json')
    put = client.put(
        base_ddo_url + '/%s' % json.loads(post.data.decode('utf-8'))['id'],
        data=json.dumps(json_update),
        content_type='application/json')
    rv = client.get(
        base_ddo_url + '/%s' % json.loads(post.data.decode('utf-8'))['id'],
        content_type='application/json')
    assert 200 == put.status_code
    assert json_update['service'][2]['attributes']['curation']['numVotes'] == \
           json.loads(rv.data.decode('utf-8'))['service'][0]['attributes']['curation']['numVotes']
    assert json.loads(post.data.decode('utf-8'))['service'][0]['attributes']['main'][
               'checksum'] != \
           json.loads(rv.data.decode('utf-8'))['service'][0]['attributes']['main'][
               'checksum']
    client.delete(
        base_ddo_url + '/%s' % json.loads(post.data.decode('utf-8'))['id'])


def test_query_metadata(client, base_ddo_url, test_assets):
    assert len(json.loads(client.post(base_ddo_url + '/query',
                                      data=json.dumps({}),
                                      content_type='application/json').data.decode('utf-8'))[
                   'results']) == 2
    assert len(json.loads(client.post(base_ddo_url + '/query',
                                      data=json.dumps(
                                          { "bool": {"must": [{"range": {
                                           "service.attributes.main.price": {"gte": 14,
                                                                             "lte": 16}}}]}}),
                                      content_type='application/json').data.decode('utf-8'))[
                   'results']) == 2
    assert len(json.loads(client.post(base_ddo_url + '/query',
                                      data=json.dumps(
                                          {"bool": {
                                            "should": [{"match": {"_id": "did:nv:"
                                                                        ":0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e430"}}
                                                    ]}}),
                                      content_type='application/json').data.decode('utf-8'))[
                   'results']) == 2
    assert len(json.loads(client.post(base_ddo_url + '/query',
                                      data=json.dumps(
                                          {"bool": {
                                            "should": [{"match": {"_id": "did:nv:"
                                                                        ":0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e430"}},
                                                    {"match": {"_id": "did:nv"
                                                                        ":0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e431"}}
                                                    ]}}),
                                      content_type='application/json').data.decode('utf-8'))[
                   'results']) == 2
    assert len(json.loads(client.get(base_ddo_url + '/query?text=Office',
                                     ).data.decode('utf-8'))['results']) == 1
    assert len(json.loads(
        client.get(
            base_ddo_url +
            '/query?text=0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e431',
            ).data.decode('utf-8'))['results']) == 1
    try:
        num_assets = len(test_assets) + 2
        for a in test_assets:
            client.post(base_ddo_url,
                        data=json.dumps(a),
                        content_type='application/json')

        response = json.loads(
            client.get(base_ddo_url + '/query?text=Met&page=1&offset=5', )
                .data.decode('utf-8')
        )
        assert response['page'] == 1
        assert response['total_pages'] == int(num_assets / 5) + int(num_assets % 5 > 0)
        assert response['total_results'] == num_assets
        assert len(response['results']) == 5

        response = json.loads(
            client.get(base_ddo_url + '/query?text=Met&page=3&offset=5', )
                .data.decode('utf-8')
        )
        assert response['page'] == 3
        assert response['total_pages'] == int(num_assets / 5) + int(num_assets % 5 > 0)
        assert response['total_results'] == num_assets
        assert len(response['results']) == num_assets - (5 * (response['total_pages'] - 1))

        response = json.loads(
            client.get(base_ddo_url + '/query?text=Met&page=4&offset=5', )
                .data.decode('utf-8')
        )
        assert response['page'] == 4
        assert response['total_pages'] == int(num_assets / 5) + int(num_assets % 5 > 0)
        assert response['total_results'] == num_assets
        assert len(response['results']) == 0

    finally:
        for a in test_assets:
            client.delete(BaseURLs.BASE_METADATA_URL + '/assets/ddo/%s' % a['id'])


def test_delete_all(client_with_no_data, base_ddo_url, json_dict, json_update):
    client_with_no_data.post(base_ddo_url,
                             data=json.dumps(json_dict),
                             content_type='application/json')
    client_with_no_data.post(base_ddo_url,
                             data=json.dumps(json_update),
                             content_type='application/json')
    assert len(json.loads(
        client_with_no_data.get(BaseURLs.BASE_METADATA_URL + '/assets').data.decode('utf-8'))[
                   'ids']) == 2
    client_with_no_data.delete(base_ddo_url)
    assert len(json.loads(
        client_with_no_data.get(BaseURLs.BASE_METADATA_URL + '/assets').data.decode('utf-8'))[
                   'ids']) == 0


def test_is_listed(client, base_ddo_url, json_dict, json_dict2):
    assert len(json.loads(
        client.get(BaseURLs.BASE_METADATA_URL + '/assets').data.decode('utf-8'))['ids']
               ) == 2

    client.put(
        base_ddo_url + '/%s' % json_dict['id'],
        data=json.dumps(json_dict2),
        content_type='application/json')
    assert len(json.loads(
        client.get(BaseURLs.BASE_METADATA_URL + '/assets').data.decode('utf-8'))['ids']
               ) == 1
    assert len(json.loads(
        client.post(base_ddo_url + '/query',
                    data=json.dumps({ "bool": {"must": [{"range": {
                                           "service.attributes.main.price": {"gte": 14,
                                                                             "lte": 16}}}]}}),
                    content_type='application/json').data.decode('utf-8')
    )['results']) == 1
    assert len(json.loads(
        client.post(base_ddo_url + '/query',
                    data=json.dumps({"query": {}, "show_unlisted": False}),
                    content_type='application/json').data.decode('utf-8')
    )['results']) == 1
    assert len(json.loads(
        client.post(base_ddo_url + '/query',
                    data=json.dumps({"query": {}, "show_unlisted": True}),
                    content_type='application/json').data.decode('utf-8')
    )['results']) == 2

def test_agreement_creation_and_retrieval(client, base_agreement_url, json_agreement):
    client.post(base_agreement_url,
                data=json.dumps(json_agreement),
                content_type='application/json')
    print(client.get(base_agreement_url + '/%s' % json_agreement['agreementId']).data.decode('utf-8'))
    assert json.loads(
        client.get(base_agreement_url + '/%s' % json_agreement['agreementId']).data.decode('utf-8'))['price'] == 23


def test_date_format_validator():
    date = '2016-02-08T16:02:20Z'
    assert validate_date_format(date) == (None, None)


def test_invalid_date():
    date = 'XXXX'
    assert validate_date_format(date) == (
        "Incorrect data format, should be '%Y-%m-%dT%H:%M:%SZ'", 400)
