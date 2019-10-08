#!/usr/bin/python

import csv
import struct
from datamap import Translator
from remeha_core import FrameDecoder


if __name__ == '__main__':
    inputFile = open("data.csv", mode="r")
    csv_reader = csv.reader(inputFile)
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
                output_csv_data = [translator.translate("Date")]
                for valuetype_and_value in list_of_valuetype_and_value:
                    output_csv_data += ['"' + translator.translate(valuetype_and_value[0]) + '"']

                new_row = ','.join(str(e) for e in output_csv_data)
                print(new_row)

            output_csv_data = [row[0]]
            for valuetype_and_value in list_of_valuetype_and_value:
                output_csv_data += [valuetype_and_value[1]]

            new_row = ','.join(str(e) for e in output_csv_data)
            print(new_row)
