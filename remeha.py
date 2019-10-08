#!/usr/bin/env python
import serial
import time
import csv
import os
import sys
import argparse

from mqtt_logger import LogToMQtt
from remeha_core import Frame

"""
All I known about a frame:
General format: "startbyte header data checksum endbyte", in little-endian
startbyte/stopbyte aka magic bytes: frame starts with 02 and ends with 03. Also seen recom sending frames which start
with 07 and end with 0xd2 (probably for another protocol), no more infos on this second kind of frame
header:
    is 6 bytes long
    the first to bytes of the header of the response are always the swapped two bytes from request.
         Probably some kind of source/destination address?
         if it really is an address, then Recom software uses 0xFE, the "master" aka boiler is 0x00 and
              sample data is request from 0x01 (PCU?)
         not sure how the number of devices and the addresses are detected. Maybe some are fixed and always there?
              maybe some of them are identified by identification messages of the fixed devices?
    Byte 3 is always 05 for the request and 06 for the response
    byte 4 is the frame size. The frame size includes the checksum, but not the start/stop bytes.
    Byte 5 and 6 look like type info for the data part of the frame, not sure if 2 separate bytes or one 2 byte value
       0x01 0x0B (0x0b01) identification
       0x02 0x01 (0x0102) sample data
       0x10 0x1C (0x1C10) Counter data
            0x1F
       0x10 0x14 (0x1410) Parameter data
            0x1B
data: at least for sample-data it depends on the device type, so the identification should be requested and processed
frame has a two byte (crc16) checksum before the end magic (0x03).

"""


class FileLogger:
    def __init__(self, filename):
        is_new_file = not os.path.isfile(filename)
        self.log_file = open(filename, "a")

        self.csv_writer = csv.writer(self.log_file)
        if is_new_file:
            self.csv_writer.writerow(["timestamp", "SourceAddress", "FrameType", "Frame length"])

    def log_data(self, frame):
        frame_data = frame.get_data()
        row = [str(frame.timestamp), str(frame.get_source_address()), str(frame.get_type()), str(len(frame_data))]
        row += frame_data
        self.csv_writer.writerow(row)


def log(source_serial, destination_filename, mqtt_freq):
    ser = serial.Serial(source_serial,
                        9600,
                        timeout=10,
                        parity='N',
                        bytesize=8,
                        stopbits=1
                        )
    if not ser.isOpen():
        sys.exit("Could not open serial: " + source_serial)

    log_mqtt = LogToMQtt(mqtt_freq)
    log_file = FileLogger(destination_filename)

    sample_data_request: bytes = bytes([0x02, 0xFE, 0x01, 0x05, 0x08, 0x02, 0x01, 0x69, 0xAB, 0x03])
    last_frame_was_valid = True
    runtime_seconds = 0
    while True:
        # sys.stdout.flush()
        ser.write(sample_data_request)

        frame = Frame(io_source=ser)
        if frame.isValid:
            last_frame_was_valid = True
            log_file.log_data(frame)
            log_mqtt.log(frame, runtime_seconds)

            while ser.inWaiting():
                unknown_data = ser.read(ser.inWaiting())
                print("Error unknown data: " + unknown_data.hex())
                time.sleep(1)
        else:
            if not last_frame_was_valid:
                sys.exit("Two consecutive read errors")
            print("Sleep and retry")
            time.sleep(10)
            ser.close()
            time.sleep(10)
            ser.open()
            last_frame_was_valid = False
        runtime_seconds += 1
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Log data from Remeha boiler')
    parser.add_argument('-d', '--device', default="/dev/ttyS0",
                        help='serial device the boiler is connected to. i.e. /dev/ttyUSB0 [Default: %(default)s]')
    parser.add_argument('-o', '--output', default="data.csv", help='file to log the data to [Default: %(default)s]')
    parser.add_argument('-m', '--mqtt_freq', type=int, default="15",
                        help='frequency for publishing MQTT data in seconds [Default: %(default)s]')
    args = parser.parse_args()

    log(args.device, args.output, args.mqtt_freq)
