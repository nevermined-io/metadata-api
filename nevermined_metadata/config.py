import configparser
import logging
import os

from nevermined_metadata.constants import ConfigSections

DEFAULT_NAME_METADATA_URL = 'http://localhost:5000'

NAME_METADATA_URL = 'metadata.url'
ALLOW_FREE_ASSETS_ONLY = 'allowFreeAssetsOnly'
MODULE = 'module'
DB_HOSTNAME = 'db.hostname'
DB_PORT = 'db.port'

environ_names = {
    NAME_METADATA_URL: ['METADATA_URL', 'Metadata URL'],
}

config_defaults = {
    ConfigSections.RESOURCES: {
        NAME_METADATA_URL: DEFAULT_NAME_METADATA_URL,
    }
}


class Config(configparser.ConfigParser):

    def __init__(self, filename=None, **kwargs):
        configparser.ConfigParser.__init__(self)

        self.read_dict(config_defaults)
        self._section_name = ConfigSections.RESOURCES
        self._metadatadb_name = ConfigSections.METADATADB
        self._metadatadb_external_name = ConfigSections.EXTERNAL
        self._logger = kwargs.get('logger', logging.getLogger(__name__))
        self._logger.debug('Config: loading config file %s', filename)

        if filename:
            with open(filename) as fp:
                text = fp.read()
                self.read_string(text)
        else:
            if 'text' in kwargs:
                self.read_string(kwargs['text'])
        self._load_environ()

    def _load_environ(self):
        for option_name, environ_item in environ_names.items():
            value = os.environ.get(environ_item[0])
            if value is not None:
                self._logger.debug('Config: setting environ %s = %s', option_name, value)
                self.set(self._section_name, option_name, value)

    def set_arguments(self, items):
        for name, value in items.items():
            if value is not None:
                self._logger.debug('Config: setting argument %s = %s', name, value)

                self.set(self._section_name, name, value)

    @property
    def metadata_url(self):
        return self.get(self._section_name, NAME_METADATA_URL)

    @property
    def allow_free_assets_only(self):
        return self.get(self._section_name, ALLOW_FREE_ASSETS_ONLY)

    @property
    def db_url(self):
        return self.get(self._metadatadb_name, DB_HOSTNAME) + ":" + self.get(self._metadatadb_name,
                                                                             DB_PORT)

    @property
    def module(self):
        return self.get(self._metadatadb_name, MODULE)

    @property
    def module_external(self):
        try:
            return self.get(self._metadatadb_external_name, MODULE)
        except configparser.NoSectionError:
            return None

    # static methods

    @staticmethod
    def get_environ_help():
        result = []
        for option_name, environ_item in environ_names.items():
            # codacy fix
            assert option_name
            result.append("{:20}{:40}".format(environ_item[0], environ_item[1]))
        return "\n".join(result)
