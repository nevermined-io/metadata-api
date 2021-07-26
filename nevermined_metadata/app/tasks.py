import logging
import time

from uwsgidecorators import timer

from nevermined_metadata.app.dao import get_dao
from nevermined_metadata.run import app

logger = logging.getLogger(__name__)


@timer(60)
def check_status(_num):
    logger.info('Checking status of external assets...')
    with app.app_context():
        get_dao().update_external_status()
