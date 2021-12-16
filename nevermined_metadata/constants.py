class ConfigSections:
    METADATADB = 'metadatadb'
    RESOURCES = 'resources'
    EXTERNAL = 'metadatadb-external'
    AGREEMENTS = 'service-agreements'


class BaseURLs:
    BASE_METADATA_URL = '/api/v1/metadata'
    SWAGGER_URL = '/api/v1/docs'  # URL for exposing Swagger UI (without trailing '/')
    ASSETS_URL = BASE_METADATA_URL + '/assets'


class Metadata:
    TITLE = 'Nevermined metadata'
    DESCRIPTION = 'Nevermined metadata provides an off-chain database store for metadata about ' \
                  'data assets. ' \
                  'When running with our Docker images, it is exposed under:'
