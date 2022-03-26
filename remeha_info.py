#!/usr/bin/env python
import logging

import serial
import struct
from datamap import datamap_identification
import sys
import argparse

from remeha_core import Frame

log = logging.getLogger(__name__)


def eprint(*arguments, **kwargs):
    print(*arguments, file=sys.stderr, **kwargs)


class SendFrame:
    def __init__(self):
        self.frame = None

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


class RequestFrame(SendFrame):
    def __init__(self, destination_address, frame_type):
        self.frame = bytearray([0x02, 0xFE, destination_address, 0x05, 0x08])
        self.frame.append(frame_type & 0xFF)
        self.frame.append((frame_type >> 8) & 0xFF)
        self.add_checksum()
        self.frame.append(0x03)

    def get_frame_data(self):
        return self.frame


class FrameDecoder:
    def __init__(self):
        self.data_hash = {}
        self.unpack_with_format = "<" + ''.join(entry[0] for entry in datamap_identification)

    def decode_all(self, data):
        if len(data) >= 64:
            unpacked_data = list(struct.unpack(self.unpack_with_format, data))
            return unpacked_data
        return []

    def decode_to_dict(self, data):
        result_map = {}
        for index, value in enumerate(self.decode_all(data)):
            value = datamap_identification[index][1](value)
            log.debug("{}: {}".format(datamap_identification[index][3], value))
            value_name = datamap_identification[index][2]
            if not value_name.startswith('unknown'):
                result_map[value_name] = value

        return result_map


def request_device_identification(io_device, address):
    log.info(f"Requesting info from device with address {address}")
    identification_frame = RequestFrame(address, 0x0B01)

    test_the_frame = Frame(frame_data=identification_frame.get_frame_data())
    decoded_data = {}
    # ensure the crc is right
    if test_the_frame.isValid:
        io_device.write(identification_frame.get_frame_data())
        identification_response = Frame(io_source=io_device)
        if identification_response.isValid:
            log.debug(identification_response)
            as_string = [chr(x) for x in identification_response.get_framedata()]
            log.debug(as_string)
            decoded_data = FrameDecoder().decode_to_dict(identification_response.get_data())
            log.debug(decoded_data)
    else:
        log.warning(f"Request frame not valid: {test_the_frame}")
    return decoded_data


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
    parser.add_argument('-v', '--verbose', action='store_true', help='Be very verbose')
    parser.add_argument('-q', '--quiet', action='store_true', help='No infos. Just error and warnings')

    args = parser.parse_args()
    loglevel = logging.DEBUG if args.verbose else logging.INFO
    loglevel = logging.WARNING if args.quiet else loglevel
    logging.basicConfig(level=loglevel, format='%(message)s')

    request_infos(args.device)
