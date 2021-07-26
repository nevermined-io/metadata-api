import pytest

from nevermined_metadata.app.dao import Dao


@pytest.fixture
def dao():
    return Dao(config_file='./tests/resources/config-test-external.ini')