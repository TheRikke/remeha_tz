import datetime
import json
from os import path
from unittest import TestCase, mock
from unittest.mock import call

from mqtt_logger import LogToMQtt
from remeha import Frame


class TestLogToMQtt(TestCase):
    unpacked_test_data = [0, 1, 2, 10, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                          0,  # status
                          0,  # locking
                          1,  # blocking
                          2,  # substatus
                          ]
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ensure we always use the english texts for tests
        self.patcher = mock.patch('datamap.locale')
        self.locale_mock = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.locale_mock.getlocale.return_value = ['en_US', 'UTF8']
        self.default_config = json.loads(
            """{ "mqtt_logger": { "enabled": true, "host": "localhost", "port": 1883, "topic": "boiler",
              "log_values": ["outside_temp", "flow_temp", "return_temp", "status", "substatus", "locking", "blocking",
               "calorifier_temp", "airflow_actual"],
              "Log_values_with_duration": [ {"value_name": "status", "expected_value": "burning_dhw"}]}}
            """)

    def __del__(self, *args, **kwargs):
        self.locale_mock.stop()

    def test_connect_to_config_server(self):
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(json.loads(
                """{ "mqtt_logger": { "enabled": true, "host": "myhost", "port": 1234, "topic": "boiler",
                  "log_values": ["test_value"],
                  "Log_values_with_duration": []}}
                """), 5)

            sut.log_single_value('outside_temp', TestLogToMQtt.unpacked_test_data)
            mqtt_mock.connect.assert_called_once_with(host="myhost", port=1234)

    def test_log_single_value(self):
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            sut.log_single_value('outside_temp', TestLogToMQtt.unpacked_test_data)
            mqtt_mock.publish.assert_called_once_with('boiler/outside_temp', '0.1', retain=True)

    def test_log_single_value__with_last_change_time(self):
        """
        test a integer value with info of last change
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            sut.log_single_value('outside_temp', TestLogToMQtt.unpacked_test_data, datetime.datetime.now())
            mqtt_mock.publish.assert_called_once_with('boiler/outside_temp', '0.1 (0s)', retain=True)

    def test_log_single_value__with_last_change_time_string(self):
        """
        test case where the value to post with mqtt is a string
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, datetime.datetime.now())
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (0s)', retain=True)

    def test_log_single_value__with_last_change_time_string_on_change(self):
        """
        test case where the value to post with mqtt is a string
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, datetime.datetime.now())
            changed_data = TestLogToMQtt.unpacked_test_data
            changed_data[26] += 1
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (0s)', retain=True)
            mqtt_mock.reset_mock()
            sut.log_single_value('status', changed_data, datetime.datetime.now())
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Boiler start (0s)', retain=True)

    def test_log_single_value__with_last_change_time_string__updates_time(self):
        """
        test case where the value to post with mqtt is increases the "not changed since"
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            current_date = datetime.datetime.now()
            update_date = current_date + datetime.timedelta(minutes=2)
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, current_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (0s)', retain=True)
            mqtt_mock.reset_mock()
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, update_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (2min)', retain=True)

    def test_log_single_value__with_last_change_time_string__long_updates_time(self):
        """
        test case where the value to post with mqtt is increases the "not changed since"
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            current_date = datetime.datetime.now()
            update_date = current_date + datetime.timedelta(hours=10)
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, current_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (0s)', retain=True)
            mqtt_mock.reset_mock()
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, update_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (10h)', retain=True)

    def test_log_single_value__scale(self):
        """
        test case where the value to post with mqtt is increases the "not changed since"
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            TestLogToMQtt.unpacked_test_data[3] = 10  # 0.1
            sut.log_single_value('outside_temp', TestLogToMQtt.unpacked_test_data, scale_to_percent=[0, 1])
            mqtt_mock.publish.assert_called_once_with('boiler/outside_temp', '10.0', retain=True)

    def test_log_single_value__scale_from_config(self):
        """
        test case where the value to post with mqtt is increases the "not changed since"
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(json.loads("""{ "mqtt_logger": { "enabled": true, "host": "localhost", "port": 1883,
                "topic": "boiler",
                "log_values": ["outside_temp"],
                "scale_to_percent": [
                    {
                        "value_name": "outside_temp",
                        "lower_limit": 0,
                        "upper_limit": 1
                    }
                ]
              }}
            """), 5)

            TestLogToMQtt.raw_test_data[13] = 10
            TestLogToMQtt.raw_test_data[14] = 0
            # update checksum
            TestLogToMQtt.raw_test_data[71] = 0x61
            TestLogToMQtt.raw_test_data[72] = 0xed
            sut.log(Frame(frame_data=TestLogToMQtt.raw_test_data), 0)

            mqtt_mock.publish.assert_called_once_with('boiler/outside_temp', '10.0', retain=True)

    def test_log_single_value_when_disabled_config(self):
        """
        test case where the value to post with mqtt is increases the "not changed since"
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(json.loads("""{ "mqtt_logger": { "enabled": false}}"""), 5)

            sut.log(Frame(frame_data=TestLogToMQtt.raw_test_data), 0)
            mqtt_mock.publish.assert_not_called()

    def test_log_single_value_when_no_config(self):
        """
        test case where the value to post with mqtt is increases the "not changed since"
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(json.loads("""{}"""), 5)
            sut.log(Frame(frame_data=TestLogToMQtt.raw_test_data), 0)

            mqtt_mock.publish.assert_not_called()

    def test_default_config(self):
        """
        test the default config causes the right values to be logged
        """
        with open(path.join(path.dirname(path.realpath(__file__)), "..", "config", "remeha.conf")) as json_file:
            with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
                mqtt_mock.Client.return_value = mqtt_mock
                sut = LogToMQtt(json.load(json_file), 5)

                TestLogToMQtt.raw_test_data[13] = 10
                TestLogToMQtt.raw_test_data[14] = 0
                # update checksum
                TestLogToMQtt.raw_test_data[71] = 0x61
                TestLogToMQtt.raw_test_data[72] = 0xed
                sut.log(Frame(frame_data=TestLogToMQtt.raw_test_data), 0)

                calls = [call('boiler/outside_temp', '0.1', retain=True),
                         call('boiler/flow_temp', '47.7', retain=True),
                         call('boiler/return_temp', '25.6', retain=True),
                         call('boiler/calorifier_temp', '48.6', retain=True),
                         call('boiler/airflow_actual', '83.1', retain=True),
                         call('boiler/status', 'Burning CH (0s)', retain=True),
                         call('boiler/substatus', 'Normal internal setpoint (0s)', retain=True),
                         call('boiler/locking', 'No locking (0s)', retain=True),
                         call('boiler/blocking', 'No Blocking (0s)', retain=True)]
                mqtt_mock.publish.assert_has_calls(calls)

    def test_log(self):
        """
        test case where the value to post with mqtt is a string
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            sut.log(Frame(frame_data=TestLogToMQtt.raw_test_data), 0)
            mqtt_mock.publish.assert_called()

    def test_log_duration_of_value_start(self):
        """
        test case where
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            current_date = datetime.datetime.now()
            sut.log_duration_of_value('status', 'Standby', TestLogToMQtt.unpacked_test_data, current_date)
            mqtt_mock.publish.assert_not_called()

    def test_log_duration_of_value_only_updates_after_a_full_cycle(self):
        """
        test case where
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(self.default_config, 5)

            current_date = datetime.datetime.now()
            update_date_1 = current_date + datetime.timedelta(seconds=1)
            update_date_2 = update_date_1 + datetime.timedelta(seconds=1)
            # Set status to burning_dhw
            TestLogToMQtt.unpacked_test_data[26] = 4
            sut.log_duration_of_value('status', 'burning_dhw', TestLogToMQtt.unpacked_test_data, current_date)
            sut.log_duration_of_value('status', 'burning_dhw', TestLogToMQtt.unpacked_test_data, update_date_1)
            TestLogToMQtt.unpacked_test_data[26] = 0
            sut.log_duration_of_value('status', 'burning_dhw', TestLogToMQtt.unpacked_test_data, update_date_2)
            mqtt_mock.publish.assert_called_once_with('boiler/status_burning_dhw_duration', '2s', retain=True)
