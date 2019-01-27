#!/usr/bin/python
import serial
import socket
import struct
import time
import sys
import time
from datetime import datetime
import csv
import os
from datamap import datamap, fmt
#from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# All I known about a frame:
# General format: "startbyte header data checksum endbyte", in little-endian
# startbyte/stopbyte aka magic bytes: frame starts with 02 and ends with 03. Also seen recom sending frames which start with 07  and end with 0xd2  (probably for other protocol), no more infos on this second kind of frame
# header:
#     is 6 bytes long
#     the first to bytes of the header of the response are always the swapped two bytes from request. Probably some kind of source/destination address?
#          if it really is an address, then recom software uses 0xFE, the "master" aka boiler is 0x00. sample data is request from 0x01 (PCU?)
#          not sure how the number of devices and the addresses are detected. Maybe some are fixed and always there? and maybe some of them areidentified by identification messages of the fixed devices?
#     Byte 3 is always 05 for the request and 06 for the response
#     byte 4 is the frame size. The frame size includes the checksum, but not the start/stop bytes.
#     Byte 5 and 6 look like type info for the data part of the frame, not sure if 2 separate bytes or one 2 byte value
#        0x01 0x0B (0x0b01) identification
#        0x02 0x01 (0x0102) sample data
#        0x10 0x1C (0x1C10) Counter data
#             0x1F
#        0x10 0x14 (0x1410) Parameter data
#             0x1B
# data: at least for sample-data is dependend of the device type, so the identification should be requested and processed
# frame has a two byte (crc16) checksum before the end magic (0x03)
class Frame:
    def __init__(self, io_source):
        self.isValid = False
        self.frame = io_source.read(7)   #read header first
        self.timestamp = datetime.now()


        if len(self.frame) < 7 or not (self.frame[0]==2 or self.frame[0]==7):
            print("Could not read the whole frame header")
            return None

        size = 2 + self.frame[4]   # start and end magic are not factored in

        self.frame += io_source.read(size - 7)

        if len(self.frame) < size:
            eprint("Could not read a whole frame of size %d" % (size))
            return None

        if (self.frame[0]==2 and self.frame[-1] != 3) or (self.frame[0]==7 and self.frame[-1] != 0xd2):
            eprint("Frame start/stop magic incorrect")
            return None

        check_sum = 0xFF;

        if self.get_checksum(self.frame) != struct.unpack("<H", self.frame[-3:-1])[0]:
            eprint("Checksum incorrect")
            return None
        self.isValid = True

    def get_checksum(self, frame):
        crc = 0xFFFF
        for data_byte in frame[1:-3]:
            crc ^= data_byte
            for counter in range(0,8):
                if (crc & 0x0001) !=0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def get_framedata(self):
        return self.frame

    def get_data(self):
        return self.frame[7:-3]

    def get_type(self):
        return struct.unpack("<H", self.frame[5:7])[0]

    def get_readable_type(self):
        return self.frame[8:-3]

    def get_source_address(self):
        return self.frame[1]

class FileLogger:
    def __init__(self, filename):
        is_new_file = not os.path.isfile(filename)
        self.log_file = open(filename, "a")

        self.csv_writer = csv.writer(self.log_file)
        if is_new_file:
            self.csv_writer.writerow([ "timestamp", "SourceAddress", "FrameType", "Frame length" ])

    def log_data(self, frame):
        frame_data = frame.get_data()
        row = [ str(frame.timestamp), str(frame.get_source_address()), str(frame.get_type()), str(len(frame_data)) ]
        row += frame_data
        self.csv_writer.writerow(row)
        self.log_file.flush()

def log(source_serial, destination_filename):
    ser = serial.Serial(source_serial,
        9600,
        timeout=10,
        parity='N',
        bytesize=8,
        stopbits=1
    )
    if not ser.isOpen():
        sys.exit("Could not open serial: " + source_serial)

    sample_data_request = bytes([ 0x02, 0xFE, 0x01, 0x05, 0x08, 0x02, 0x01, 0x69, 0xAB, 0x03 ])
    log_file = FileLogger(destination_filename)
    while True:
        #sys.stdout.flush()
        ser.write(sample_data_request)

        frame = Frame(ser)

        if frame.isValid:
            log_file.log_data(frame)

            print("known data: " + frame.get_framedata().hex())
            #print(struct.unpack(fmt, frame.get_framedata()))

            #stats = list(parse_data(unpacked))
            #for stat in stats:
            #    s = 'cv.{}:{}|{}'.format(*stat)
            #    print(stat)

            while ser.inWaiting():
                unknowndata = ser.read(ser.inWaiting())
                print ("Error unknown data: " + unknowndata.hex())
                time.sleep(1)
        else:
            sys.exit("Error reading frame")
        #assert not ser.inWaiting()
        time.sleep(1)

if __name__ == "__main__":
    log("/dev/ttyS0", "data.csv")
