import logging
from datetime import datetime
import struct
import sys

from datamap import datamap

log = logging.getLogger(__name__)


def eprint(*arguments, **kwargs):
    print(*arguments, file=sys.stderr, **kwargs)


def parse_data(input_data, map_resolve=True):
    for n, x in enumerate(input_data):
        value = datamap[n][1](x)
        #        print("Value: " + str(value))
        if isinstance(value, list):
            for sub_index, sub_value in enumerate(value):
                # if i[0]:
                yield [datamap[n][2][sub_index], sub_value]
        elif map_resolve and isinstance(datamap[n][4], dict) and value in datamap[n][4]:
            yield [datamap[n][2], datamap[n][4][value]]
        else:
            yield [datamap[n][2], value]


class Frame:
    def __init__(self, io_source=None, frame_data=None):
        self.isValid = False
        self.frame = None
        if io_source:
            self.frame = io_source.read(7)  # read header first
        elif frame_data:
            self.frame = frame_data
        else:
            print("Error need to provide a reading source or the data directly")
            return
        self.timestamp = datetime.now()

        if len(self.frame) < 7 or not (self.frame[0] == 2 or self.frame[0] == 7):
            print("Could not read the whole frame header")
            return

        size = 2 + self.frame[4]  # start and end magic are not factored in

        if io_source:
            self.frame += io_source.read(size - 7)

        if len(self.frame) < size:
            eprint("Could not read a whole frame of size %d" % size)
            return

        if (self.frame[0] == 2 and self.frame[-1] != 3) or (self.frame[0] == 7 and self.frame[-1] != 0xd2):
            eprint("Frame start/stop magic incorrect")
            return

        if self.get_checksum() != struct.unpack("<H", self.frame[-3:-1])[0]:
            eprint("Checksum incorrect. Should be {:x}, but is {:x}"
                   .format(self.get_checksum(), struct.unpack("<H", self.frame[-3:-1])[0]))
            return

        self.isValid = True
        self.unpack_with_format = "<" + ''.join(entry[0] for entry in datamap)

    def __str__(self):
        return ''.join('{:02x} '.format(x) for x in self.frame)

    def get_checksum(self):
        crc = 0xFFFF
        for data_byte in self.frame[1:-3]:
            crc ^= data_byte
            for counter in range(0, 8):
                if (crc & 0x0001) != 0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def get_framedata(self):
        return self.frame

    def get_parseddata(self, ):
        return list(struct.unpack(self.unpack_with_format, self.frame[7:-3]))

    def get_data(self):
        return self.frame[7:-3]

    def get_type(self):
        return struct.unpack("<H", self.frame[5:7])[0]

    def get_readable_type(self):
        return self.frame[8:-3]

    def get_source_address(self):
        return self.frame[1]


class FrameDecoder:
    def __init__(self):
        self.unpack_with_format = "<" + ''.join(entry[0] for entry in datamap)
        self.data_hash = {}
        for value_index, element in enumerate(datamap):
            name_i = element[2]
            if isinstance(name_i, list):
                for sub_value_index, sub_element in enumerate(name_i):
                    self.data_hash[sub_element] = [[value_index, sub_value_index]] + element
            else:
                self.data_hash[name_i] = [value_index] + element

    def decode(self, unpacked_raw_values, value_name):
        decoder_data = self.data_hash[value_name]
        if isinstance(decoder_data[5], dict):
            index_in_unpacked_raw_values = decoder_data[0]
            converted_value = decoder_data[2](unpacked_raw_values[index_in_unpacked_raw_values])
            return decoder_data[5][converted_value]
        else:
            return decoder_data[2](unpacked_raw_values[decoder_data[0]])

    def decode_all(self, packed_raw_values):
        return list(parse_data(struct.unpack(self.unpack_with_format, packed_raw_values)))

    def get_unpacked_data(self, packed_raw_values):
        return list(struct.unpack(self.unpack_with_format, packed_raw_values))
