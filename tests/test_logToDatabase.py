import datetime
import logging
from unittest import TestCase, mock
from database_logger import DatabaseLogger, log
from remeha import Frame

class TestLogToDatabase(TestCase):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ensure we always use the english texts for tests
        self.patcher = mock.patch('database_logger.mysql.connector')
        self.database_mock = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.cursor_mock = mock.MagicMock()
        self.insert_cursor_mock = mock.MagicMock()
        self.mock_result = mock.MagicMock()
        self.database_mock.connect.return_value = self.cursor_mock
        self.cursor_mock.cursor.return_value = self.insert_cursor_mock

    def __del__(self, *args, **kwargs):
        self.database_mock.stop()

    def test_log_all_values(self):
        sut = DatabaseLogger()
        log.setLevel(logging.DEBUG)
        sut.log_data(Frame(frame_data=TestLogToDatabase.raw_test_data))
        self.insert_cursor_mock.execute.assert_called_with('INSERT INTO boiler_data (flow_temp, return_temp, dhw_in_temp, outside_temp, calorifier_temp, boiler_control_temp, room_temp, cv_setpoint, dhw_setpoint, room_setpoint, airflow_setpoint, airflow_actual, ionisation_current, intern_setpoint, output, pump_speed, setpoint_power, actual_power, dwh_heat_demand, anti_legionella, dhw_blocking, dhw_eco_boiler_not_kept_warm, frost_protection, heat_demand, modulating_controller_demand, modulating_controller, dhw_enabled, ch_enabled, min_gas_pressure, flow_switch_for_detecting_dhw, ionisation, release_input, shutdown_input, ext_gas_valve, ext_three_way_valve, three_way_valve, ignition, gas_valve, opentherm_smart_power, status_report, ext_ch_pump, calorifier_pump, pump, status, locking, blocking, substatus, fan_speed, su_state, su_locking, su_blocking, hydr_pressure, dhw_timer_enable, ch_timer_enable, hru_active, control_temp, dhw_flow, solar_temp, hmi_active, ch_setpoint_hmi, dhw_setpoint_hmi, service_mode, serial_mode, whole_frame) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (47.7, 25.6, -32.0, 4.5, 48.6, 37.4, 17.45, 47.5, 50.0, 22.0, 2408, 2410, 5.800000000000001, 47.5, 71, 69, 100, 71, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 'burning_ch', 'no_locking', 'no_blocking', 'normal_internal_setpoint', 3888, 4, -1, -1, 0.0, 1, 1, 0, 46.86, 0.0, -3276.8, 839, 64, 53, 0, 0, b'\xa2\x12\x00\n\x80\xf3\xc2\x01\xfc\x12\x00\x80\x9c\x0e\xd1\x06\x8e\x12\x88\x13\x98\x08h\tj\t:\x8e\x12GE\x00dG\x00\x00\x13\xc6@\x05\x03\xff\xff\x1e0\x0f\x04\xff\xff\x00\xc0N\x12\x00\x00\x00\x00\x80G\x03@5\x00\x00'))
        assert not self.database_mock.commit.called
