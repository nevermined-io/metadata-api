import copy
import json
import logging
from datetime import datetime

from flask import Blueprint, jsonify, request, Response
from metadatadb_driver_interface.search_model import FullTextModel, QueryModel

from nevermined_metadata.app.dao import Dao
from nevermined_metadata.config import Config
from nevermined_metadata.log import setup_logging
from nevermined_metadata.myapp import app

setup_logging()
assets = Blueprint('assets', __name__)

# Prepare MetadataDB
dao = Dao(config_file=app.config['CONFIG_FILE'])
logger = logging.getLogger('metadata')


@assets.route('', methods=['GET'])
def get_assets():
    """
    Get all asset IDs.
    swagger_from_file: docs/get_assets.yml
    """
    args = []
    query = dict()
    args.append(query)
    asset_with_id = dao.get_all_listed_assets()
    asset_ids = [a['id'] for a in asset_with_id]
    resp_body = dict({'ids': asset_ids})
    return Response(_sanitize_record(resp_body), 200, content_type='application/json')


@assets.route('/ddo/<did>', methods=['GET'])
def get_ddo(did):
    """Get DDO of a particular asset.
    swagger_from_file: docs/get_ddo.yml
    """
    try:
        asset_record = dao.get(did)
        return Response(_sanitize_record(asset_record), 200, content_type='application/json')
    except Exception as e:
        logger.error(e)
        return f'{did} asset DID is not in MetadataDB', 404


@assets.route('/metadata/<did>', methods=['GET'])
def get_metadata(did):
    """Get metadata of a particular asset
    swagger_from_file: docs/get_metadata.yml
    """
    try:
        asset_record = dao.get(did)
        metadata = _get_metadata(asset_record['service'])
        return Response(_sanitize_record(metadata), 200, content_type='application/json')
    except Exception as e:
        logger.error(e)
        return f'{did} asset DID is not in MetadataDB', 404


@assets.route('/ddo', methods=['POST'])
def register():
    """Register DDO of a new asset
    swagger_from_file: docs/register.yml
    """
    assert isinstance(request.json, dict), 'invalid payload format.'
    required_attributes = ['@context', 'created', 'id', 'publicKey', 'authentication', 'proof',
                           'service']
    data = request.json
    if not data:
        logger.error(f'request body seems empty.')
        return 400
    msg, status = check_required_attributes(required_attributes, data, 'register')
    if msg:
        return msg, status
    msg, status = check_no_urls_in_files(_get_main_metadata(data['service']), 'register')
    if msg:
        return msg, status
    msg, status = validate_date_format(data['created'])
    if status:
        return msg, status
    _record = dict()
    _record = copy.deepcopy(data)
    _record['created'] = datetime.strptime(data['created'], '%Y-%m-%dT%H:%M:%SZ')
    for service in _record['service']:
        if service['type'] == 'metadata':
            service_id = int(service['index'])
            if Config(filename=app.config['CONFIG_FILE']).allow_free_assets_only == 'true':
                if _record['service'][service_id]['attributes']['main']['price'] != "0":
                    logger.warning('Priced assets are not supported in this marketplace')
                    return 'Priced assets are not supported in this marketplace', 400
            _record['service'][service_id]['attributes']['main']['dateCreated'] = \
                datetime.strptime(
                    _record['service'][service_id]['attributes']['main']['dateCreated'],
                    '%Y-%m-%dT%H:%M:%SZ')
            _record['service'][service_id]['attributes']['curation'] = {}
            _record['service'][service_id]['attributes']['curation']['rating'] = 0.00
            _record['service'][service_id]['attributes']['curation']['numVotes'] = 0
            _record['service'][service_id]['attributes']['curation']['isListed'] = True
    _record['service'] = _reorder_services(_record['service'])
    # if not is_valid_dict_remote(_get_metadata(_record['service'])['attributes']):
    #     logger.error(
    #         _list_errors(list_errors_dict_remote,
    #                      _get_metadata(_record['service'])['attributes']))
    #     return jsonify(_list_errors(list_errors_dict_remote,
    #                                 _get_metadata(_record['service'])['attributes'])), 400
    try:
        dao.register(_record, data['id'])
        # add new assetId to response
        return Response(_sanitize_record(_record), 201, content_type='application/json')
    except Exception as err:
        logger.error(f'encounterd an error while saving the asset data to MetadataDB: {str(err)}')
        return f'Some error: {str(err)}', 500


@assets.route('/ddo/<did>', methods=['PUT'])
def update(did):
    """Update DDO of an existing asset
    swagger_from_file: docs/update.yml
    """
    required_attributes = ['@context', 'created', 'id', 'publicKey', 'authentication', 'proof',
                           'service']
    assert isinstance(request.json, dict), 'invalid payload format.'
    data = request.json
    if not data:
        logger.error(f'request body seems empty, expecting {required_attributes}')
        return 400
    msg, status = check_required_attributes(required_attributes, data, 'update')
    if msg:
        return msg, status
    msg, status = check_no_urls_in_files(_get_main_metadata(data['service']), 'register')
    if msg:
        return msg, status
    msg, status = validate_date_format(data['created'])
    if msg:
        return msg, status
    _record = dict()
    _record = copy.deepcopy(data)
    _record['created'] = datetime.strptime(data['created'], '%Y-%m-%dT%H:%M:%SZ')
    _record['service'] = _reorder_services(_record['service'])

    try:
        for service in _record['service']:
            if service['type'] == 'metadata':
                if Config(filename=app.config['CONFIG_FILE']).allow_free_assets_only == 'true':
                    if _record['service'][0]['attributes']['main']['price'] != "0":
                        logger.warning('Priced assets are not supported in this marketplace')
                        return 'Priced assets are not supported in this marketplace', 400
        dao.update(_record, did)
        return Response(_sanitize_record(_record), 200, content_type='application/json')
    except Exception as err:
        return f'Some error: {str(err)}', 500


@assets.route('/ddo/<did>', methods=['DELETE'])
def retire(did):
    """Retire metadata of an asset
    swagger_from_file: docs/retire.yml
    """
    try:
        if dao.get(did) is None:
            return 'This asset DID is not in MetadataDB', 404
        else:
            dao.delete(did)
            return 'Succesfully deleted', 200
    except Exception as err:
        return f'Some error: {str(err)}', 500


@assets.route('/ddo', methods=['GET'])
def get_asset_ddos():
    """Get DDO of all assets.
    swagger_from_file: docs/get_asset_ddos.yml
    """
    args = []
    query = dict()
    args.append(query)
    assets_with_id = dao.get_all_listed_assets()
    assets_metadata = {a['id']: a for a in assets_with_id}
    for i in assets_metadata:
        _sanitize_record(i)
    return Response(json.dumps(assets_metadata, default=_my_converter), 200,
                    content_type='application/json')


@assets.route('/ddo/query', methods=['GET'])
def query_text():
    """Get a list of DDOs that match with the given text.
     swagger_from_file: docs/query_text.yml
    """
    data = request.args
    assert isinstance(data, dict), 'invalid `args` type, should already formatted into a dict.'
    search_model = FullTextModel(text=data.get('text', None),
                                 sort=None if data.get('sort', None) is None else json.loads(
                                     data.get('sort', None)),
                                 offset=int(data.get('offset', 100)),
                                 page=int(data.get('page', 1)))
    query_result = dao.query(search_model, data.get('show_unlisted'))
    for i in query_result[0]:
        _sanitize_record(i)
    response = _make_paginate_response(query_result, search_model)
    return Response(json.dumps(response, default=_my_converter), 200,
                    content_type='application/json')


@assets.route('/ddo/query', methods=['POST'])
def query_ddo():
    """Get a list of DDOs that match with the executed query.
     swagger_from_file: docs/query_ddo.yml
    """
    assert isinstance(request.json, dict), 'invalid payload format.'
    data = request.json
    assert isinstance(data, dict), 'invalid `body` type, should be formatted as a dict.'
    if 'query' in data:
        search_model = QueryModel(query=data.get('query'), sort=data.get('sort'),
                                  offset=data.get('offset', 100),
                                  page=data.get('page', 1))
    else:
        search_model = QueryModel(query={}, sort=data.get('sort'),
                                  offset=data.get('offset', 100),
                                  page=data.get('page', 1))
    query_result = dao.query(search_model, data.get('show_unlisted'))
    for i in query_result[0]:
        _sanitize_record(i)
    response = _make_paginate_response(query_result, search_model)
    return Response(json.dumps(response, default=_my_converter), 200,
                    content_type='application/json')


@assets.route('/ddo', methods=['DELETE'])
def retire_all():
    """Retire metadata of all the assets.
     swagger_from_file: docs/retire_all.yml
    """
    try:
        all_ids = [a['id'] for a in dao.get_all_assets()]
        for i in all_ids:
            dao.delete(i)
        return 'All ddo successfully deleted', 200
    except Exception as e:
        logger.error(e)
        return 'An error was found', 500


def _sanitize_record(data_record):
    if '_id' in data_record:
        data_record.pop('_id')
    return json.dumps(data_record, default=_my_converter)


def check_required_attributes(required_attributes, data, method):
    assert isinstance(data, dict), 'invalid `body` type, should already formatted into a dict.'
    logger.info('got %s request: %s' % (method, data))
    if not data:
        logger.error('%s request failed: data is empty.' % method)
        logger.error('%s request failed: data is empty.' % method)
        return 'payload seems empty.', 400
    for attr in required_attributes:
        if attr not in data:
            logger.error('%s request failed: required attr %s missing.' % (method, attr))
            return '"%s" is required in the call to %s' % (attr, method), 400
    return None, None


def check_no_urls_in_files(main, method):
    if 'files' in main:
        for file in main['files']:
            if 'url' in file:
                logger.error('%s request failed: url is not allowed in files ' % method)
                return '%s request failed: url is not allowed in files ' % method, 400
    return None, None


def _get_metadata(services):
    for service in services:
        if service['type'] == 'metadata':
            return service


def _get_main_metadata(services):
    return _get_metadata(services)['attributes']['main']


def _get_curation_metadata(services):
    return _get_metadata(services)['attributes']['curation']


def validate_date_format(date):
    try:
        datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        return None, None
    except Exception as e:
        logging.error(str(e))
        return "Incorrect data format, should be '%Y-%m-%dT%H:%M:%SZ'", 400


def _my_converter(o):
    if isinstance(o, datetime):
        return o.strftime('%Y-%m-%dT%H:%M:%SZ')


def _make_paginate_response(query_list_result, search_model):
    total = query_list_result[1]
    offset = search_model.offset
    result = dict()
    result['results'] = query_list_result[0]
    result['page'] = search_model.page

    result['total_pages'] = int(total / offset) + int(total % offset > 0)
    result['total_results'] = total
    return result


def _reorder_services(services):
    result = []
    for service in services:
        if service['type'] == 'metadata':
            result.append(service)
    for service in services:
        if service['type'] != 'metadata':
            result.append(service)
    return result
