#!/usr/bin/python
import serial
import socket
import struct
import time
import sys
import time

from datamap import datamap, fmt

ser = serial.Serial('/dev/ttyUSB0',
    9600,
    timeout=10,
    parity='N',
    bytesize=8,
    stopbits=1
)
print ('serial open', ser.isOpen())

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#addr = ('localhost', 8125)
#print 'udp %s' % str(addr)

string = b"\x02\xFE\x01\x05\x08\x02\x01\x69\xAB\x03"
header_format = '<8B'

def get_checksum(frame):
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

# known about a frame "startbyte header data checksum endbyte", in little-endian
# startbyte/stopbyte aka magic bytes: frame starts with 02 and ends with 03. Also seen recom sending frames which start with 07  and end with 0xd2  (probably for other protocol), no more infos on this kind of frame
# header:
#     is 6 bytes long
#     the first to bytes of the header of the response are always the swapped two bytes from request. Probably some kind of source/destination address?
#          if it really is an address, then recom is 0xFE, the "master" aka boiler is 0x00. sample data is request from 0x01
#          not sure how the number and addresses are detected, maybe some are fixed and always there? and maybe some of them areidentified by identification messages of the fixed devices?
#     Byte 3 is always 05 for the request and 06 for the response
#     byte 4 is the frame size. The frame size includes the checksum, but not the start/stop bytes.
#     Byte 5 and 6 look like type info for the data part of the frame, not sure if 2 separate bytes or one 2 byte value
#        0x01 0x0B (0x0b01) identification
#        0x02 0x01 (0x0102) sample data
#        0x10 0x1C (0x1C10) Counter data
#             0x1F
#        0x10 0x14 (0x1410) Parameter data
#             0x1B
#
# frame has a two byte (crc16) checksum before the end magic (0x03)
class Frame:
    def __init__(self, io_source):
        self.frame = io_source.read(7)   #read header first

        if len(self.frame) < 7 or not (self.frame[0]==2 or self.frame[0]==7):
            return None

        size = 2 + self.frame[4]   # start and end magic are not factored in

        self.frame += io_source.read(size - 7)

        if len(self.frame) < size:
            print("Could not read a whole frame of size %d" % (size))
            return None

        if (self.frame[0]==2 and self.frame[-1] != 3) or (self.frame[0]==7 and self.frame[-1] != 0xd2):
            print("Frame start/stop magic incorrect")
            return None

        check_sum = 0xFF;

        if get_checksum(self.frame) != struct.unpack("<H", self.frame[-3:-1])[0]:
            print("Checksum incorrect")
            return None

    def get_framedata(self):
        return self.frame

    def get_data(self):
        return self.frame[7:-3]

    def get_type(self):
        return struct.unpack("<H", self.frame[:-3]

    def get_readable_type(self):
        return self.frame[8:-3]

def parse_data(data):
    for n, x in enumerate(data):
        value = datamap[n][1](x)
        print("Value: " + str(value))
        if isinstance(value, map):
            for i in zip(datamap[n][2], value, datamap[n][5]):
                if i[0]:
                    yield i
        elif datamap[n][2]:
            if int(value) < 0:
                yield datamap[n][2], value, datamap[n][5]
            yield datamap[n][2], value, datamap[n][5]

log_file = open("data.bin", "ab")

while True:
    sys.stdout.flush()
    ser.write(string)

    frame = Frame(ser)

    #log_data(logfile, frame)

#    if frame.isValid():
#        writeToFile(logfile, frame)

    #end = time.time()
    #print(end - start)

    print("known data: " + frame.get_data().hex())
    #while len(frame) < 74:
    #    frame += ser.read(ser.inWaiting())

    log_file.write(frame.get_data())
    print(struct.unpack(fmt, frame.get_data()))

    #stats = list(parse_data(unpacked))
    #for stat in stats:
    #    s = 'cv.{}:{}|{}'.format(*stat)
    #    print(stat)

    while ser.inWaiting():
        unknowndata = ser.read(ser.inWaiting())
        print ("Error unknown data: " + unknowndata.hex())
        time.sleep(1)
    #assert not ser.inWaiting()
    time.sleep(1)

#print('kthxbye')
