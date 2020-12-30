import json
from unittest import mock
from unittest.mock import patch, call

from database_logger import DatabaseLogger
from remeha import Frame
import mysql.connector

from tests.test_base import TestBase


class TestLogToDatabase(TestBase):
    unpacked_test_data = [0, 1, 2, 10, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                          0,  # status
                          0,  # locking
                          1,  # blocking
                          2,  # substatus
                          ]
    raw_test_data = bytes([0x02, 0x01, 0xfe, 0x06, 0x48, 0x02, 0x01, 0xa2,
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
        self.cursor_mocks = []

    @patch('database_logger.mysql.connector')
    def test_log_all_values(self, connector_mock):
        config = '{ "database_logger": { "enabled": true, "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } }'
        cursor_mock = mock.MagicMock()
        insert_cursor_mock = mock.MagicMock()
        connector_mock.connect.return_value = cursor_mock
        cursor_mock.cursor.return_value = insert_cursor_mock

        sut = DatabaseLogger(json.loads(config))
        sut.log_data(Frame(frame_data=TestLogToDatabase.raw_test_data))
        insert_cursor_mock.execute.assert_called_with((
            'INSERT INTO boiler_data ('
            'flow_temp, return_temp, dhw_in_temp, outside_temp, calorifier_temp, boiler_control_temp, room_temp, '
            'cv_setpoint, dhw_setpoint, room_setpoint, airflow_setpoint, airflow_actual, ionisation_current, '
            'intern_setpoint, output, pump_speed, setpoint_power, actual_power, dwh_heat_demand, anti_legionella, '
            'dhw_blocking, dhw_eco_boiler_not_kept_warm, frost_protection, heat_demand, modulating_controller_demand, '
            'modulating_controller, dhw_enabled, ch_enabled, min_gas_pressure, flow_switch_for_detecting_dhw, '
            'ionisation, release_input, shutdown_input, ext_gas_valve, ext_three_way_valve, three_way_valve, ignition, '
            'gas_valve, opentherm_smart_power, status_report, ext_ch_pump, calorifier_pump, pump, status, locking, '
            'blocking, substatus, fan_speed, su_state, su_locking, su_blocking, hydr_pressure, dhw_timer_enable, '
            'ch_timer_enable, hru_active, control_temp, dhw_flow, solar_temp, hmi_active, ch_setpoint_hmi, '
            'dhw_setpoint_hmi, service_mode, serial_mode, whole_frame) VALUES '
            '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'),
            (47.7, 25.6, -32.0, 4.5, 48.6, 37.4, 17.45, 47.5, 50.0, 22.0, 2408, 2410, 5.800000000000001, 47.5, 71,
            69, 100, 71, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 3, 255, 255, 30,
            3888, 4, -1, -1, 0.0, 1, 1, 0, 46.86, 0.0, -3276.8, 839, 64, 53, 0, 0,
            b'\xa2\x12\x00\n\x80\xf3\xc2\x01\xfc\x12\x00\x80\x9c\x0e\xd1\x06\x8e\x12\x88\x13\x98\x08h\tj\t:\x8e\x12GE\x00dG\x00\x00\x13\xc6@\x05\x03\xff\xff\x1e0\x0f\x04\xff\xff\x00\xc0N\x12\x00\x00\x00\x00\x80G\x03@5\x00\x00'))

    @patch('database_logger.mysql.connector')
    def test_fail_on_missing_database_config(self, connector_mock):
        config = '{ "database_logger": { "enabled": true, "host": "testserver.local" } }'

        sut = DatabaseLogger(json.loads(config))
        sut.log_data(Frame(frame_data=TestLogToDatabase.raw_test_data))
        assert not connector_mock.execute.called

    @patch('database_logger.mysql.connector.connect')
    def test_do_not_crash_on_access_denied(self, connect_mock):
        config = '{ "database_logger": { "enabled": true, "host": "1", "user_name": "2", "password": "3" } }'
        connect_mock.side_effect = mysql.connector.errors.ProgrammingError()
        DatabaseLogger(json.loads(config))

    @patch('database_logger.mysql.connector')
    def test_when_database_usage_disabled_then_do_not_use_database(self, connector_mock):
        config = '{ "database_logger": { "enabled": false, "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } }'

        sut = DatabaseLogger(json.loads(config))
        sut.log_data(Frame(frame_data=TestLogToDatabase.raw_test_data))
        assert not connector_mock.connect.called

    def add_mocks(self, prepared=None):
        new_mock = mock.MagicMock()
        new_mock.with_rows = False
        self.cursor_mocks += [new_mock]
        return new_mock

    def get_mock(self, table_name, insert_mock=False):
        for mock_to_check in self.cursor_mocks:
            for execute_calls in mock_to_check.method_calls:
                if execute_calls[0] == 'execute':
                    if insert_mock:
                        for call_str in execute_calls[1]:
                            if call_str.startswith("INSERT INTO {}".format(table_name)):
                                return mock_to_check
                    else:
                        if execute_calls == call.execute("SHOW TABLES LIKE '{}'".format(table_name)):
                            return mock_to_check
        return mock.MagicMock()

    @patch('database_logger.mysql.connector')
    def test_table_creation_boiler_data(self, connector_mock):
        config = '{ "database_logger": { "enabled": true, "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } }'
        remeha_db_mock = mock.MagicMock()
        connector_mock.connect.return_value = remeha_db_mock
        remeha_db_mock.cursor.side_effect = self.add_mocks
        DatabaseLogger(json.loads(config))
        mock_to_check = self.get_mock('boiler_data')
        calls = [
            call("SHOW TABLES LIKE 'boiler_data'"),
            call('CREATE TABLE boiler_data (time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, flow_temp FLOAT, return_temp FLOAT, dhw_in_temp FLOAT, outside_temp FLOAT, calorifier_temp FLOAT, boiler_control_temp FLOAT, room_temp FLOAT, cv_setpoint FLOAT, dhw_setpoint FLOAT, room_setpoint FLOAT, airflow_setpoint FLOAT, airflow_actual FLOAT, ionisation_current FLOAT, intern_setpoint FLOAT, output FLOAT, pump_speed FLOAT, setpoint_power FLOAT, actual_power FLOAT, dwh_heat_demand BOOL, anti_legionella BOOL, dhw_blocking BOOL, dhw_eco_boiler_not_kept_warm BOOL, frost_protection BOOL, heat_demand BOOL, modulating_controller_demand BOOL, modulating_controller BOOL, dhw_enabled BOOL, ch_enabled BOOL, min_gas_pressure BOOL, flow_switch_for_detecting_dhw BOOL, ionisation BOOL, release_input BOOL, shutdown_input BOOL, ext_gas_valve BOOL, ext_three_way_valve BOOL, three_way_valve BOOL, ignition BOOL, gas_valve BOOL, opentherm_smart_power BOOL, status_report BOOL, ext_ch_pump BOOL, calorifier_pump BOOL, pump BOOL, status TINYINT UNSIGNED, locking TINYINT UNSIGNED, blocking TINYINT UNSIGNED, substatus TINYINT UNSIGNED, fan_speed FLOAT, su_state FLOAT, su_locking FLOAT, su_blocking FLOAT, hydr_pressure FLOAT, dhw_timer_enable BOOL, ch_timer_enable BOOL, hru_active BOOL, control_temp FLOAT, dhw_flow FLOAT, solar_temp FLOAT, hmi_active FLOAT, ch_setpoint_hmi FLOAT, dhw_setpoint_hmi FLOAT, service_mode FLOAT, serial_mode FLOAT, whole_frame TINYBLOB);'),
        ]
        mock_to_check.execute.assert_has_calls(calls, any_order=False)

    @patch('database_logger.mysql.connector')
    def test_table_creation_status_mapped(self, connector_mock):
        config = '{ "database_logger": { "enabled": true, "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } }'
        remeha_db_mock = mock.MagicMock()
        connector_mock.connect.return_value = remeha_db_mock
        remeha_db_mock.cursor.side_effect = self.add_mocks
        DatabaseLogger(json.loads(config))
        mock_to_check = self.get_mock('status_mapped')
        calls = [
            call("SHOW TABLES LIKE 'status_mapped'"),
            call('CREATE TABLE status_mapped (value INT KEY, name TINYTEXT);'),
            call("INSERT INTO status_mapped (value,name) VALUES (0,'Standby'),(1,'boiler_start'),(2,'burner_start'),(3,'burning_ch'),(4,'burning_dhw'),(5,'burner_stop'),(6,'boiler_stop'),(8,'controlled_stop'),(9,'blocking_mode'),(10,'locking_mode'),(11,'chimney_mode_1'),(12,'chimney_mode_2'),(13,'chimney_mode_3'),(15,'manual_heat_demand'),(16,'boiler_frost_protection'),(17,'de_aeration'),(18,'controller_temp_protection');)"),
        ]
        mock_to_check.execute.assert_has_calls(calls, any_order=False)

    @patch('database_logger.mysql.connector')
    def test_create_table_log_manual(self, connector_mock):
        config = '{ "database_logger": { "enabled": true, "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } }'
        db_mock = mock.MagicMock()
        connector_mock.connect.return_value = db_mock
        db_mock.cursor.side_effect = self.add_mocks
        DatabaseLogger(json.loads(config))

        self.get_mock('manual_data').execute.assert_has_calls([
            call("SHOW TABLES LIKE 'manual_data'"),
            call('CREATE TABLE manual_data (time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, message TEXT);'),
        ], any_order=False)

    @patch('database_logger.mysql.connector')
    def test_log_manual(self, connector_mock):
        config = '{ "database_logger": { "enabled": true, "host": "testserver.local", "user_name": "database_user", "password": "secret_passwort" } }'
        cursor_mock = mock.MagicMock()
        connector_mock.connect.return_value = cursor_mock
        cursor_mock.cursor.side_effect = self.add_mocks
        sut = DatabaseLogger(json.loads(config))
        sut.log_manual("test message")

        self.get_mock('manual_data', insert_mock=True).execute.assert_has_calls([
            call('INSERT INTO manual_data (message) VALUES (%s);', params=('test message',))
        ], any_order=False)
