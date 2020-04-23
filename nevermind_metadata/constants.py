#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

class ConfigSections:
    OCEANBD = 'oceandb'
    RESOURCES = 'resources'


class BaseURLs:
    BASE_METADATA_URL = '/api/v1/metadata'
    SWAGGER_URL = '/api/v1/docs'  # URL for exposing Swagger UI (without trailing '/')
    ASSETS_URL = BASE_METADATA_URL + '/assets'


class Metadata:
    TITLE = 'Nevermind metadata'
    DESCRIPTION = 'Nevermind metadata provides an off-chain database store for metadata about ' \
                  'data assets. ' \
                  'When running with our Docker images, it is exposed under:'
