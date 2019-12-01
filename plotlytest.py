#!/usr/bin/env python
import datetime
import threading

import dash
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import csv
import struct
from dash.dependencies import Input, Output
from datamap import datamap
from datamap import Translator

import argparse

log_setting = 1


def log(log_priority, message):
    if log_priority <= log_setting:
        print("%s: %s" % (datetime.datetime.now().time(), message))


interval = 60 * 60 * 1000
data_dates = []
data = []
data_mapped_values = {}
data_description = []
read_lock = threading.Lock()
fig = None

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--verbose', action='store_true', help='increase verbosity')
parser.add_argument('--debug', action='store_true', help='run flask server in debug mode')
parser.add_argument('-m', '--max-read', type=int, default=1024, help='maximum to read in kb [Default: %(default)s]')
parser.add_argument('-p', '--max-points', type=int, default=50,
                    help='maximum data points to hold [Default: %(default)s]')
parser.add_argument('-i', '--input', default="data.csv", help='file read the data from [Default: %(default)s]')
args = parser.parse_args()

if args.verbose:
    log_setting = 0

inputFile = open(args.input, mode="r")
csv_reader = csv.reader(inputFile)
csv_pos = 0
fmt = "<" + ''.join(entry[0] for entry in datamap)


app = dash.Dash()

app.layout = html.Div(children=[
    html.Div([
        dcc.RadioItems(id='set-time',
                       value=60 * 60 * 1000,
                       options=[
                           {'label': 'Every second', 'value': 1000},
                           {'label': 'Every 5 seconds', 'value': 5000},
                           {'label': 'Off', 'value': 60 * 60 * 1000}  # or just every hour
                       ]),
        dcc.Checklist(
            id='checklist',
            options=[{'label': 'on', 'value': 1}],
            value=[2]
        ),
    ]),
    html.H1("Plotly test with Live update",
            style={"font-family": "Helvetica",
                   "border-bottom": "1px #000000 solid"}),
    html.Div(children='''
                    Dash: A web application framework for Python.
                '''),
    html.Div(dcc.Graph(id='plot', style={'height': '80vh'}), style={'height': '100vh'}),
    #                dcc.Slider(
    #                    id='year-slider',
    #                    min=df['year'].min(),
    #                    max=df['year'].max(),
    #                    value=df['year'].min(),
    #                    marks={str(year): str(year) for year in df['year'].unique()}
    #                ),

    #                html.Div([dcc.Graph(id='plot2'),]),
    dcc.Interval(id='live-update', interval=interval, n_intervals=0),
], )


@app.callback(Output('live-update', 'interval'), [Input('set-time', 'value')])
def update_interval(value):
    return value


@app.callback(Output('plot', 'figure'), [Input('live-update', 'n_intervals')])
def gen_plot(n):
    log(0, "gen_plot: {}".format(n))
    global data
    global fig
    if read_lock.acquire(blocking=False):

        if read_data(data, csv_reader) or n == 0:
            to_delete = len(data[0]) - args.max_points
            if to_delete > 0:
                log(2, "Delete %d points" % to_delete)
                for values in data:
                    del values[to_delete:]

            log(1, "Number of samples %d in %d traces" % (len(data[0]), len(data)))
            trace = []
            for index, values in enumerate(data):
                log(3, "Group: %s" % data_description[index][1])
                if index > 0:
                    # legendgroup='group2',
                    # if to_delete > 0:
                    #     del data[index][to_delete:]
                    log(1, "add trace {}".format(index))
                    if data_description[index][1] == "temps":
                        trace += [go.Scatter(x=data[0], y=data[index], yaxis='y3', name=data_description[index][0],
                                             line=dict(width=1))]
                    elif data_description[index][1] == "flow":
                        trace += [go.Scatter(x=data[0], y=data[index], yaxis='y2',
                                             name=data_description[index][0], line=dict(width=1))]
                    elif data_description[index][1] == "switch" or\
                            data_description[index][1] == "mapped" or\
                            data_description[index][1] == "unknown":
                        if index in data_mapped_values:
                            trace += [go.Scatter(x=data[0], y=data[index], text=data_mapped_values[index],
                                                 name=data_description[index][0], line=dict(width=1))]
                        else:
                            trace += [go.Scatter(x=data[0], y=data[index], name=data_description[index][0],
                                                 line=dict(width=1))]
                    log(1, "traces created")
                    layout = go.Layout(
                        title="Heating at Home",
                        uirevision=1,
                        yaxis=dict(domain=[0, 0.10]),
                        yaxis2=dict(domain=[0.10, 0.5]),
                        yaxis3=dict(domain=[0.5, 1]),
                    )
            fig = dict(data=trace, layout=layout)
        else:
            log(1, "No new data read")
    else:
        log(1, "already updating")
        read_lock.acquire()
    read_lock.release()
    return fig


def parse_data(input_data):
    for n, x in enumerate(input_data):
        value = datamap[n][1](x)
        #        print("Value: " + str(value))
        if isinstance(value, list):
            for i in value:
                # if i[0]:
                yield i
        elif datamap[n][2]:
            yield value


def read_data(data, csv_reader):
    #    DateAndTimeToParse = datetime.now() - timedelta(hours=1)
    #    firstValidDateFound = False
    #    errorCount = 0
    skipCount = 0
    readCount = 0
    for row in csv_reader:
        readCount += 1
        if row[2] == "258" and len(row) >= 68:
            integer_list = [int(value) for value in row[4:]]
            packed_data = bytes(struct.pack(str(len(row) - 4) + "B", *integer_list))
            parsed_data = list(parse_data(struct.unpack(fmt, packed_data)))

            data[0] += [row[0]]
            for index, value in enumerate(parsed_data):
                data[index + 1] += [value]

                # print(index)
                # print(datamap[index])
                if index + 1 in data_mapped_values:
                    # print(data_mapped_values)
                    # print(data_description[index + 1])

                    data_mapped_values[index + 1] += [data_description[index + 1][2][value]]
        else:
            skipCount += 1
    # print("New rows: %d" % readCount)
    # print(data_mapped_values)

    disabled_counter = 0
    for index, data_element in enumerate(data):
        set_test_all_the_same = set(data_element)
        if len(set_test_all_the_same) == 1:
            log(0, "Disable {}, all values the same: {}".format(data_description[index][0], set_test_all_the_same))
            data_description[index][1] = 'disabled'
            disabled_counter += 1
    log(0, "Disabled {} traces with all zero values".format(disabled_counter))
    return readCount > 0


def skipIfToMuch(fileToSkip, maximumInKb):
    maxDataToReadInitially = maximumInKb * 1024
    fileToSkip.seek(0, 2)
    newPosition = fileToSkip.tell() - maxDataToReadInitially
    if newPosition < 0:
        newPosition = 0
    fileToSkip.seek(newPosition)
    fileToSkip.readline()


# for date
data += [[]]
data_description += [["date_time", "none"]]
value_index = 0
translator = Translator()
for map_entry in datamap:
    #        print("Value: " + str(value))
    if isinstance(map_entry[2], list):
        for index, description in enumerate(map_entry[3]):
            data += [[]]
            data_description += [[str(description), str(map_entry[4][index])]]
            value_index += 1
    else:
        data += [[]]
        data_description += [[str(translator.translate(map_entry[2])), str(map_entry[3]), map_entry[4]]]
        value_index += 1

    if isinstance(map_entry[4], dict):
        # print("Add index: {}".format(value_index))
        data_mapped_values[value_index] = []

skipIfToMuch(inputFile, args.max_read)
read_data(data, csv_reader)
log(0, "dash core component version: %s" % dcc.__version__)

app.run_server(host="0.0.0.0", debug=args.debug)
