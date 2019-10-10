import datetime
from unittest import TestCase, mock
from mqtt_logger import LogToMQtt
from remeha import Frame


class TestLogToMQtt(TestCase):
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
        self.patcher = mock.patch('datamap.locale')
        self.locale_mock = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.locale_mock.getlocale.return_value = ['en_US', 'UTF8']

    def __del__(self, *args, **kwargs):
        self.locale_mock.stop()

    def test_log_single_value(self):
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(5)

            sut.log_single_value('outside_temp', TestLogToMQtt.unpacked_test_data)
            mqtt_mock.publish.assert_called_once_with('boiler/outside_temp', '0.1', retain=True)

    def test_log_single_value__with_last_change_time(self):
        """
        test a integer value with info of last change
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(5)

            sut.log_single_value('outside_temp', TestLogToMQtt.unpacked_test_data, datetime.datetime.now())
            mqtt_mock.publish.assert_called_once_with('boiler/outside_temp', '0.1 (0s)', retain=True)

    def test_log_single_value__with_last_change_time_string(self):
        """
        test case where the value to post with mqtt is a string
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(5)

            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, datetime.datetime.now())
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (0s)', retain=True)

    def test_log_single_value__with_last_change_time_string_on_change(self):
        """
        test case where the value to post with mqtt is a string
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(5)

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
            sut = LogToMQtt(5)

            current_date = datetime.datetime.now()
            update_date = current_date + datetime.timedelta(minutes=1)
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, current_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (0s)', retain=True)
            mqtt_mock.reset_mock()
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, update_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (1min)', retain=True)

    def test_log_single_value__with_last_change_time_string__updates_time(self):
        """
        test case where the value to post with mqtt is increases the "not changed since"
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(5)

            current_date = datetime.datetime.now()
            update_date = current_date + datetime.timedelta(hours=10)
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, current_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (0s)', retain=True)
            mqtt_mock.reset_mock()
            sut.log_single_value('status', TestLogToMQtt.unpacked_test_data, update_date)
            mqtt_mock.publish.assert_called_once_with('boiler/status', 'Standby (10h)', retain=True)

    def test_log(self):
        """
        test case where the value to post with mqtt is a string
        """
        with mock.patch('mqtt_logger.mqttClient') as mqtt_mock:
            mqtt_mock.Client.return_value = mqtt_mock
            sut = LogToMQtt(5)

            sut.log(Frame(frame_data=TestLogToMQtt.raw_test_data), 0)
            mqtt_mock.publish.assert_called()
