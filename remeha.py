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
    
    #data = ser.read(ser.inWaiting())
    #start = time.time()
    data = ser.read(74)
    
    #end = time.time()
    #print(end - start)

    print("known data: " + data.hex())
    while len(data) < 74:
        data += ser.read(ser.inWaiting())
    log_file.write(data)
    print(struct.unpack(fmt, data))

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
