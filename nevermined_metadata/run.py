import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from nevermined_metadata.app.assets import assets
from nevermined_metadata.app.info import info
from nevermined_metadata.config import Config
from nevermined_metadata.constants import BaseURLs

logger = logging.getLogger(__name__)


def create_app(config_file='config.ini'):
    app = Flask(__name__)
    CORS(app)

    # Load configuration settings
    if 'CONFIG_FILE' in os.environ and os.environ['CONFIG_FILE']:
        app.config['CONFIG_FILE'] = os.environ['CONFIG_FILE']
    else:
        logger.info('Using default config: config.ini')
        app.config['CONFIG_FILE'] = config_file

    config = Config(app.config['CONFIG_FILE'])

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        BaseURLs.SWAGGER_URL,
        config.metadata_url + '/spec',
        config={  # Swagger UI config overrides
            'app_name': "Test application"
        },
    )

    # Register blueprint at URL
    app.register_blueprint(swaggerui_blueprint, url_prefix=BaseURLs.SWAGGER_URL)
    app.register_blueprint(assets, url_prefix=BaseURLs.ASSETS_URL)
    app.register_blueprint(info, url_prefix='/')

    return app


if __name__ == '__main__':
    app = create_app()
    config = Config(app.config['CONFIG_FILE'])

    if isinstance(config.metadata_url.split(':')[-1], int):
        app.run(host=config.metadata_url.split(':')[1],
                port=config.metadata_url.split(':')[-1])
    else:
        app.run()
