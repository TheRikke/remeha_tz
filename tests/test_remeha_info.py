import datetime
import json
import logging
from os import path
from unittest import TestCase, mock
from unittest.mock import call

from remeha import Frame
from remeha_info import request_device_identification, SendFrame

log = logging.getLogger()


class TestRemehaInfo(TestCase):
    unpacked_test_data = [0, 1, 2, 10, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                          0,  # status
                          0,  # locking
                          1,  # blocking
                          2,  # substatus
                          ]
    raw_test_data = bytearray([0x02, 0x00, 0xfe, 0x06, 0x48, 0x01, 0x0b, 0x0d, 0x0b, 0x0e, 0xff, 0xff, 0x14, 0x12, 0x02,
                               0x16, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0x04, 0x05, 0xff, 0x01, 0xff, 0xff, 0xff,
                               0xff, 0x0b, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36,
                               0x37, 0x38, 0x39, 0x30, 0x31, 0x32, 0x33, 0x20, 0x20, 0x20, 0x54, 0x7a, 0x65, 0x72, 0x72,
                               0x61, 0x20, 0x45, 0x78, 0x70, 0x6f, 0x72, 0x74, 0x20, 0x20, 0x20, 0x46, 0xef, 0x03])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.setLevel(logging.DEBUG)
        self.read_offset = 0

        # update checksum
        send_frame = SendFrame()
        send_frame.frame = self.raw_test_data[:-3]
        send_frame.add_checksum()
        send_frame.frame.append(0x03)
        self.raw_test_data = send_frame.frame

    def test_connect_to_config_server(self):

        def read_method(length):
            data = self.raw_test_data[self.read_offset:self.read_offset + length]
            self.read_offset += length
            return data

        self.io_device_mock = mock.MagicMock()
        self.io_device_mock.read.side_effect = read_method
        decoded_data = request_device_identification(self.io_device_mock, address=0)
        self.assertEqual(decoded_data['serial_number'], '1234567890123')


