#!/usr/bin/env python
import argparse
import csv
import struct
from datamap import Translator
from remeha_core import FrameDecoder


def convert(csv_reader):
    first_row = True
    frame_decoder = FrameDecoder()
    translator = Translator()
    for row in csv_reader:
        if row[2] == "258" and len(row) >= 68:
            integer_list = [int(value) for value in row[4:]]
            packed_data = bytes(struct.pack(str(len(row) - 4) + "B", *integer_list))
            list_of_valuetype_and_value = frame_decoder.decode_all(packed_data)
            if first_row:
                first_row = False
                print_head_row(list_of_valuetype_and_value, translator)
            print_sample_data(list_of_valuetype_and_value, row)


def print_head_row(list_of_valuetype_and_value, translator):
    output_csv_data = [translator.translate("Date")]
    for valuetype_and_value in list_of_valuetype_and_value:
        output_csv_data += ['"' + translator.translate(valuetype_and_value[0]) + '"']

    new_row = ','.join(str(e) for e in output_csv_data)
    print(new_row)


def print_sample_data(list_of_valuetype_and_value, row):
    output_csv_data = [row[0]]
    for valuetype_and_value in list_of_valuetype_and_value:
        if isinstance(valuetype_and_value[1], (int, float)):
            output_csv_data += [valuetype_and_value[1]]
        else:
            output_csv_data += ['"' + valuetype_and_value[1] + '"']
    new_row = ','.join(str(e) for e in output_csv_data)
    print(new_row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read raw boiler data from a csv and convert to the real values')
    parser.add_argument('-i', '--input-file', default="data.csv",
                        help='file to read the raw value log from [Default: %(default)s]')
    args = parser.parse_args()

    inputFile = open(args.input_file, mode="r")

    try:
        convert(csv.reader(inputFile))
    except KeyboardInterrupt:
        pass
