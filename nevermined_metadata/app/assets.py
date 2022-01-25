import copy
import json
import logging
from datetime import datetime

from metadatadb_driver_interface.exceptions import MetadataDbError
from nevermined_metadata.app.dao import get_dao

from flask import Blueprint, request, Response, g, current_app
from metadatadb_driver_interface.search_model import FullTextModel, QueryModel

from nevermined_metadata.config import Config
from nevermined_metadata.log import setup_logging

setup_logging()
assets = Blueprint('assets', __name__)
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
    asset_with_id = get_dao().get_all_listed_assets()
    asset_ids = [a['id'] for a in asset_with_id]
    resp_body = dict({'ids': asset_ids})
    return Response(_sanitize_record(resp_body), 200, content_type='application/json')


@assets.route('/ddo/<did>', methods=['GET'])
def get_ddo(did):
    """Get DDO of a particular asset.
    swagger_from_file: docs/get_ddo.yml
    """
    try:
        asset_record = get_dao().get(did)
        return Response(
            _sanitize_record(asset_record), 200, content_type='application/json'
        )
    except Exception as e:
        logger.error(e)
        return f'{did} asset DID is not in MetadataDB', 404


@assets.route('/ddo/<did>/status', methods=['GET'])
def get_status(did):
    """Get the status of a particular DDO."""
    # TODO: Add swager definition
    try:
        status = get_dao().status(did)
        return Response(_sanitize_record(status), 200, content_type='application/json')
    except Exception as e:
        logger.error('Error fetching the status of %s: %s', did, str(e))
        return f'Error fetching the satus of {did}: {str(e)}', 500


@assets.route('/metadata/<did>', methods=['GET'])
def get_metadata(did):
    """Get metadata of a particular asset
    swagger_from_file: docs/get_metadata.yml
    """
    try:
        asset_record = get_dao().get(did)
        metadata = _get_metadata(asset_record['service'])
        return Response(
            _sanitize_record(metadata), 200, content_type='application/json'
        )
    except Exception as e:
        logger.error(e)
        return f'{did} asset DID is not in MetadataDB', 404


@assets.route('/service/<serviceId>', methods=['GET'])
def get_service(serviceId):
    """Get the Service with a particular serviceId
    swagger_from_file: docs/get_service.yml
    """
    try:
        asset_record = get_dao().get_service(serviceId)
        if not asset_record:
            return f'{serviceId} serviceId is not in MetadataDB', 404
        return Response(
            _sanitize_record(asset_record), 200, content_type='application/json'
        )
    except Exception as e:
        logger.error(e)
        return f'An exception happened during fetching of {serviceId} service.', 500

@assets.route('/service/query', methods=['POST'])
def query_service():
    """Get a list of Services that match with the executed query.
    swagger_from_file: docs/query_service.yml
    """
    assert isinstance(request.json, dict), 'invalid payload format.'
    query_model = request.json
    assert isinstance(query_model, dict), 'invalid `body` type, should be formatted as a dict.'
    
    query_result = get_dao().query_service(query_model)
    for i in query_result[0]:
        _sanitize_record(i)
    return Response(
        json.dumps(query_result, default=_my_converter),
        200,
        content_type='application/json',
    )


@assets.route('/service', methods=['POST'])
def register_service():
    """Register a Service.
    swagger_from_file: docs/register_service.yml
    """
    assert isinstance(request.json, dict), 'invalid payload format.'
    required_attributes = [
        'agreementId',
        'type',
        'index',
        'serviceEndpoint',
        'templateId',
        'attributes',
    ]
    data = request.json
    if not data:
        logger.error(f'request body seems empty.')
        return 400
    msg, status = check_required_attributes(required_attributes, data, 'register')
    if msg:
        return msg, status
    try:
        agreement_id = data.pop('agreementId')
        get_dao().persist_service(agreement_id, data)
        # add new assetId to response
        return Response(_sanitize_record(data), 201, content_type='application/json')
    except Exception as err:
        logger.error(
            f'encounterd an error while saving the Service to MetadataDB: {str(err)}'
        )
        return f'Some error: {str(err)}', 500


@assets.route('/ddo', methods=['POST'])
def register():
    """Register DDO of a new asset
    swagger_from_file: docs/register.yml
    """
    assert isinstance(request.json, dict), 'invalid payload format.'
    required_attributes = [
        '@context',
        'created',
        'id',
        'publicKey',
        'authentication',
        'proof',
        'service',
    ]
    data = request.json
    if not data:
        logger.error(f'request body seems empty.')
        return 400
    msg, status = check_required_attributes(required_attributes, data, 'register')
    if msg:
        return msg, status
    msg, status = check_no_urls_in_files(
        _get_main_metadata(data['service']), 'register'
    )
    if msg:
        return msg, status
    msg, status = validate_date_format(data['created'])
    if status:
        return msg, status

    record = _reorder_services(data)
    record = _date_to_datetime(record)

    for i, service in enumerate(record['service']):
        if service['type'] == 'metadata':
            if (
                Config(
                    filename=current_app.config['CONFIG_FILE']
                ).allow_free_assets_only
                == 'true'
            ):
                if record['service'][i]['attributes']['main']['price'] != "0":
                    logger.warning(
                        'Priced assets are not supported in this marketplace'
                    )
                    return 'Priced assets are not supported in this marketplace', 400
            record['service'][i]['attributes']['curation'] = {}
            record['service'][i]['attributes']['curation']['rating'] = 0.00
            record['service'][i]['attributes']['curation']['numVotes'] = 0
            record['service'][i]['attributes']['curation']['isListed'] = True
    try:
        get_dao().register(record, data['id'])
        # add new assetId to response
        return Response(_sanitize_record(record), 201, content_type='application/json')
    except Exception as err:
        logger.error(
            f'encounterd an error while saving the asset data to MetadataDB: {str(err)}'
        )
        return f'Some error: {str(err)}', 500


@assets.route('/ddo/<did>', methods=['PUT'])
def update(did):
    """Update DDO of an existing asset
    swagger_from_file: docs/update.yml
    """
    required_attributes = [
        '@context',
        'created',
        'id',
        'publicKey',
        'authentication',
        'proof',
        'service',
    ]
    assert isinstance(request.json, dict), 'invalid payload format.'
    data = request.json
    if not data:
        logger.error(f'request body seems empty, expecting {required_attributes}')
        return 400
    msg, status = check_required_attributes(required_attributes, data, 'update')
    if msg:
        return msg, status
    msg, status = check_no_urls_in_files(
        _get_main_metadata(data['service']), 'register'
    )
    if msg:
        return msg, status
    msg, status = validate_date_format(data['created'])
    if msg:
        return msg, status

    record = _reorder_services(data)
    record = _date_to_datetime(record)

    try:
        for service in record['service']:
            if service['type'] == 'metadata':
                if (
                    Config(
                        filename=current_app.config['CONFIG_FILE']
                    ).allow_free_assets_only
                    == 'true'
                ):
                    if record['service'][0]['attributes']['main']['price'] != "0":
                        logger.warning(
                            'Priced assets are not supported in this marketplace'
                        )
                        return (
                            'Priced assets are not supported in this marketplace',
                            400,
                        )
        get_dao().update(record, did)
        return Response(_sanitize_record(record), 200, content_type='application/json')
    except MetadataDbError as e:
        logger.warning('%s', e)
        return str(e), 405
    except Exception as err:
        return f'Some error: {str(err)}', 500


@assets.route('/ddo/<did>', methods=['DELETE'])
def retire(did):
    """Retire metadata of an asset
    swagger_from_file: docs/retire.yml
    """
    try:
        if get_dao().get(did) is None:
            return 'This asset DID is not in MetadataDB', 404
        else:
            get_dao().delete(did)
            return 'Succesfully deleted', 200
    except MetadataDbError as e:
        logger.warning('%s', e)
        return str(e), 405
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
    assets_with_id = get_dao().get_all_listed_assets()
    assets_metadata = {a['id']: a for a in assets_with_id}
    for i in assets_metadata:
        _sanitize_record(i)
    return Response(
        json.dumps(assets_metadata, default=_my_converter),
        200,
        content_type='application/json',
    )


@assets.route('/ddo/query', methods=['GET'])
def query_text():
    """Get a list of DDOs that match with the given text.
    swagger_from_file: docs/query_text.yml
    """
    data = request.args
    assert isinstance(
        data, dict
    ), 'invalid `args` type, should already formatted into a dict.'
    search_model = FullTextModel(
        text=data.get('text', None),
        sort=None
        if data.get('sort', None) is None
        else json.loads(data.get('sort', None)),
        offset=int(data.get('offset', 100)),
        page=int(data.get('page', 1)),
    )
    query_result = get_dao().query(search_model, data.get('show_unlisted'))
    for i in query_result[0]:
        _sanitize_record(i)
    response = _make_paginate_response(query_result, search_model)
    return Response(
        json.dumps(response, default=_my_converter),
        200,
        content_type='application/json',
    )


@assets.route('/ddo/query', methods=['POST'])
def query_ddo():
    """Get a list of DDOs that match with the executed query.
    swagger_from_file: docs/query_ddo.yml
    """
    assert isinstance(request.json, dict), 'invalid payload format.'
    data = request.json
    assert isinstance(data, dict), 'invalid `body` type, should be formatted as a dict.'
    if 'query' in data:
        search_model = QueryModel(
            query=data.get('query'),
            sort=data.get('sort'),
            offset=data.get('offset', 100),
            page=data.get('page', 1),
        )
    else:
        search_model = QueryModel(
            query={},
            sort=data.get('sort'),
            offset=data.get('offset', 100),
            page=data.get('page', 1),
        )
    query_result = get_dao().query(search_model, data.get('show_unlisted'))
    for i in query_result[0]:
        _sanitize_record(i)
    response = _make_paginate_response(query_result, search_model)
    return Response(
        json.dumps(response, default=_my_converter),
        200,
        content_type='application/json',
    )


@assets.route('/ddo', methods=['DELETE'])
def retire_all():
    """Retire metadata of all the assets.
    swagger_from_file: docs/retire_all.yml
    """
    try:
        all_ids = [a['id'] for a in get_dao().get_all_assets()]
        for i in all_ids:
            get_dao().delete(i)
        return 'All ddo successfully deleted', 200
    except Exception as e:
        logger.error(e)
        return 'An error was found', 500


def _date_to_datetime(asset):
    result = copy.deepcopy(asset)
    result['created'] = datetime.strptime(result['created'], '%Y-%m-%dT%H:%M:%SZ')

    for i, service in enumerate(result['service']):
        if service['type'] == 'metadata':
            result['service'][i]['attributes']['main'][
                'dateCreated'
            ] = datetime.strptime(
                result['service'][i]['attributes']['main']['dateCreated'],
                '%Y-%m-%dT%H:%M:%SZ',
            )

    return result


def _reorder_services(asset):
    services = []
    for service in asset['service']:
        if service['type'] == 'metadata':
            services.append(service)
    for service in asset['service']:
        if service['type'] != 'metadata':
            services.append(service)

    result = copy.deepcopy(asset)
    result['service'] = services

    return result


def _sanitize_record(data_record):
    if '_id' in data_record:
        data_record.pop('_id')
    return json.dumps(data_record, default=_my_converter)


def check_required_attributes(required_attributes, data, method):
    assert isinstance(
        data, dict
    ), 'invalid `body` type, should already formatted into a dict.'
    logger.info('got %s request: %s' % (method, data))
    if not data:
        logger.error('%s request failed: data is empty.' % method)
        logger.error('%s request failed: data is empty.' % method)
        return 'payload seems empty.', 400
    for attr in required_attributes:
        if attr not in data:
            logger.error(
                '%s request failed: required attr %s missing.' % (method, attr)
            )
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
