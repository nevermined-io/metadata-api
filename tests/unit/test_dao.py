import configparser
import tempfile

from nevermined_metadata.app.dao import Dao

def test_load_internal_external_plugin():
    dao = Dao(config_file='./tests/resources/config-test-external.ini')
    assert dao.metadatadb is not None
    assert dao.metadatadb_external is not None


def test_no_external():
    config_parser = configparser.ConfigParser()
    config_parser.read('./tests/resources/config-test.ini')
    config_parser.remove_section('metadatadb-external')

    with tempfile.NamedTemporaryFile(mode='w') as config_file:
        config_parser.write(config_file)
        config_file.seek(0)
        dao = Dao(config_file=config_file.name)

    assert dao.metadatadb is not None
    assert dao.metadatadb_external is None


