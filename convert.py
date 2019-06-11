#!/usr/bin/python

#import dash
#import pandas as pd
#import plotly.graph_objs as go
#import dash.dependencies as ddp
#import dash_core_components as dcc
#import dash_html_components as html
import string
import csv
import struct
#from dash.dependencies import Input, Output
from datamap import datamap, fmt

def parse_data(data):
    for n, x in enumerate(data):
        value = datamap[n][1](x)
#        print("Value: " + str(value))
        if isinstance(value, map):
            for i in zip(datamap[n][2], value, datamap[n][5]):
                if i[0]:
                    yield i
        elif datamap[n][2]:
            if int(value) < 0:
                yield datamap[n][2], value, datamap[n][5]
            yield datamap[n][2], value, datamap[n][5]


if __name__ == '__main__':
    inputFile = open("data.csv", mode = "r")
    csv_reader = csv.reader(inputFile)
#    df = pd.read_csv(inputFile, parse_dates=True)
    first_row = True
    for row in csv_reader:
        #strrow = ','.join(str(e) for e in row)
#        print("Row[2]: " + str(row[2]))
#        print(len(row))
        if row[2] == "258" and len(row) >= 64:
            integer_list = [ int(value) for value in row[4:] ]
            integer_list1 = ','.join(str(e) for e in integer_list)
#            print("intlist: " + integer_list1)
            packed_data = bytes(struct.pack( str(len(row) -4) + "B", *integer_list))
#            print("length: " + str(len(packed_data)))
            try:
                parsed_data = list(parse_data(struct.unpack(fmt, packed_data)))
            except:
                print("Error in line(%d): %s" % (len(row), row))
                continue

            if first_row:
                first_row = False
                output_csv_data = [ "Date" ]
                for data in parsed_data:
                    output_csv_data += [ data[0] ]

                new_row = ','.join(str(e) for e in output_csv_data)
                print(new_row)

            output_csv_data = [ row[0] ]
            for data in parsed_data:
                output_csv_data += [ data[1] ]

            new_row = ','.join(str(e) for e in output_csv_data)
            print(new_row)

#            print("parsed_data[0]: " + str(parsed_data[0]))
#            strrow1 = ','.join(str(e) for e in data_dates)
#            strrow2 = ','.join(str(e) for e in data_vorlauf)
#            print("Dates:" + strrow1)
#            print("Vorlauf: " + strrow2)
