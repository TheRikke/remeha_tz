import json
import os
import tempfile
from unittest import mock
from remeha import read_config, FileLogger
from remeha_core import Frame
from tests.test_base import TestBase


class TestRemeha(TestBase):

    raw_test_data = bytearray([0x02, 0x01, 0xfe, 0x06, 0x48, 0x02, 0x01, 0xa2,
                               0x12, 0x00, 0x0a, 0x80, 0xf3, 0xc2, 0x01, 0xfc,
                               0x12, 0x00, 0x80, 0x9c, 0x0e, 0xd1, 0x06, 0x8e,
                               0x12, 0x88, 0x13, 0x98, 0x08, 0x68, 0x09, 0x6a,
                               0x09, 0x3a, 0x8e, 0x12, 0x47, 0x45, 0x00, 0x64,
                               0x47, 0x00, 0x00, 0x13, 0xc6, 0x40, 0x05, 0x03,
                               0xff, 0xff, 0x1e, 0x30, 0x0f, 0x04, 0xff, 0xff,
                               0x00, 0xc0, 0x4e, 0x12, 0x00, 0x00, 0x00, 0x00,
                               0x80, 0x47, 0x03, 0x40, 0x35, 0x00, 0x00, 0x17,
                               0xef, 0x03])

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

    def test_read_config_with_special_sign(self):
        test_config_path = os.path.join(self.test_config_directory.name, 'test_config.json')
        test_config = open(test_config_path, mode='w+', encoding='utf-8')
        with mock.patch.dict('os.environ', {'REMEHA_CONF': test_config.name}):
            test_config.write('{ "database_logger": { "host": "testserver.local", "user_name": "database_user", "password": "{\\"°C\\"" } }')
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

    def test_read_default_config_if_REMEHA_CONF_not_set(self):
        with mock.patch.dict('os.environ', clear=True):
            config = read_config()
        assert config is not None

    def test_filelogger_does_nothing_if_configured_off(self):
        with mock.patch('remeha.csv') as csv_mock:
            file_logger = FileLogger(None, None)
            file_logger.log_data(self.raw_test_data)
            csv_mock.writer.assert_not_called()

    def test_filelogger_uses_filename_if_provided(self):
        with mock.patch('remeha.csv') as csv_mock:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_name = temp_dir + '/test.csv'
                file_logger = FileLogger(None, file_name)
                file_logger.log_data(Frame(frame_data=TestRemeha.raw_test_data))
                file_logger.close()
                assert os.path.exists(file_name)
                csv_mock.writer.assert_called()

    def test_filelogger_uses_config_path_if_provided(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = temp_dir + '/test.csv'
            file_logger = FileLogger(json.loads('{"enabled": true, "path": "%s"}' % file_name), None)
            file_logger.log_data(Frame(frame_data=TestRemeha.raw_test_data))
            file_logger.close()
            assert os.path.exists(file_name)

    def test_filelogger_no_file_logging_if_disabled_in_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = temp_dir + '/test.csv'
            file_logger = FileLogger(json.loads('{"enabled": false, "path": "%s"}' % file_name), None)
            file_logger.log_data(Frame(frame_data=TestRemeha.raw_test_data))
            file_logger.close()
            assert not os.path.exists(file_name)

    def test_filelogger_commandline_parameter_overwrites_config_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            expected_file_name = temp_dir + '/test.csv'
            not_expected_file_name = temp_dir + '/test2.csv'
            file_logger = FileLogger(json.loads('{"enabled": true, "path": "%s"}' % not_expected_file_name), expected_file_name)
            file_logger.log_data(Frame(frame_data=TestRemeha.raw_test_data))
            file_logger.close()
            assert not os.path.exists(not_expected_file_name)
            assert os.path.exists(expected_file_name)
