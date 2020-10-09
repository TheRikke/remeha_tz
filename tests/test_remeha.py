import os
import tempfile
from unittest import mock
from remeha import read_config
from tests.test_base import TestBase


class TestRemeha(TestBase):

    def setUp(self):
        self.test_config_directory = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.test_config_directory.cleanup()

    def test_read_config(self):
        test_config_path = os.path.join(self.test_config_directory.name, 'test_config.json')
        test_config = open(test_config_path, mode='w+')
        with mock.patch.dict('os.environ', {'REMEHA_CONF': test_config.name}):
            test_config.write('{ "database_logger": { "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } }')
            test_config.close()
            config = read_config()
        assert 'database_logger' in config

    def test_read_config_does_not_crash_on_unreadable_config(self):
        test_config_path = os.path.join(self.test_config_directory.name, 'test_config.json')
        test_config = open(test_config_path, mode='w+')
        with mock.patch.dict('os.environ', {'REMEHA_CONF': test_config.name}):
            test_config.write('{ "database_logger": { "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } ')
            test_config.close()
            config = read_config()
        assert config is None

    def test_read_default_config_if_PYCURRENT_CONF_not_set(self):
        with mock.patch.dict('os.environ', clear=True):
            config = read_config()
        assert config is None
