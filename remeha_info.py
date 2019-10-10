#!/usr/bin/env python

import serial
import struct
from datamap import datamap_identification
import sys
import argparse

from remeha_core import Frame


def eprint(*arguments, **kwargs):
    print(*arguments, file=sys.stderr, **kwargs)


class RequestFrame:
    def __init__(self, destination_address, frame_type):
        self.frame = bytearray([0x02, 0xFE, destination_address, 0x05, 0x08])
        self.frame.append(frame_type & 0xFF)
        self.frame.append((frame_type >> 8) & 0xFF)
        self.add_checksum()
        self.frame.append(0x03)

    def add_checksum(self):
        crc = 0xFFFF
        for data_byte in self.frame[1:]:
            crc ^= data_byte
            for counter in range(0, 8):
                if (crc & 0x0001) != 0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        self.frame.append(crc & 0xFF)
        self.frame.append((crc >> 8) & 0xFF)

    def get_frame_data(self):
        return self.frame


class FrameDecoder:
    def __init__(self):
        self.data_hash = {}
        for value_index, element in enumerate(datamap_identification):
            name_i = element[2]
            if isinstance(name_i, list):
                for sub_value_index, sub_element in enumerate(name_i):
                    self.data_hash[sub_element] = [[value_index, sub_value_index]] + element
            else:
                self.data_hash[name_i] = [value_index] + element
        self.unpack_with_format = "<" + ''.join(entry[0] for entry in datamap_identification)

    def decode_all(self, data):
        print(len(data))
        if len(data) == 64:
            unpacked_data = list(struct.unpack(self.unpack_with_format, data))
            print(unpacked_data)
            for index, value in enumerate(unpacked_data):
                print("{}: {}".format(datamap_identification[index][3], value))


def request_device_identification(io_device, address):
    # identification_request: bytes = bytes([0x02, 0xFE, 0x00, 0x05, 0x08, 0x01, 0x0B, 0xd4, 0x9c, 0x03])
    identification_frame = RequestFrame(address, 0x0B01)

    test_the_frame = Frame(frame_data=identification_frame.get_frame_data())
    print(test_the_frame)
    # ensure the crc is right
    if not test_the_frame.isValid:
        exit(1)
    io_device.write(identification_frame.get_frame_data())
    identification_response = Frame(io_source=io_device)
    if identification_response.isValid:
        print(identification_response)
        as_string = [chr(x) for x in identification_response.get_framedata()]
        print(as_string)
        print(FrameDecoder().decode_all(identification_response.get_data()))


def request_infos(source_serial):
    ser = serial.Serial(source_serial,
                        9600,
                        timeout=10,
                        parity='N',
                        bytesize=8,
                        stopbits=1
                        )
    if not ser.isOpen():
        sys.exit("Could not open serial: " + source_serial)

    # "02 FE 00 05 08 010B D49C 03"
    # "02 FE 01 05 08 010B E95C 03"
    # "02 FE 03 05 08 010B 909C 03"
    device_addresses_to_check = [0, 1, 2, 3, 4, 5]
    for address in device_addresses_to_check:
        request_device_identification(ser, address)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Log data from Remeha boiler')
    parser.add_argument('-d', '--device', default="/dev/ttyS0",
                        help='serial device the boiler is connected to. i.e. /dev/ttyUSB0 [Default: %(default)s]')
    args = parser.parse_args()

    request_infos(args.device)
