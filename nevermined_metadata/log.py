import logging
import logging.config
import os

import coloredlogs
import yaml


def setup_logging(default_path='logging.yaml', default_level=None, env_key='LOG_CFG'):
    """Logging Setup"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value

    if not default_level:
        level_map = {
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        default_level = level_map.get(os.getenv("LOG_LEVEL", "INFO"), logging.INFO)

    print(f'setup_logging: path={path}, level={default_level}, env-path={os.getenv(env_key, None)}')

    if os.getenv("LOG_LEVEL", None) is None and os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')
