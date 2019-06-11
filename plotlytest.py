#!/usr/bin/python

import dash
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import csv
import struct
from dash.dependencies import Input, Output
from datamap import datamap
import argparse

interval = 5000
data_dates = []
data = []
data_description = []
indexvalue = 0.3

parser = argparse.ArgumentParser(description='Process some integers.')
#parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                    help='an integer for the accumulator')
parser.add_argument('--debug',  action='store_true',   help='run in debug mode')
parser.add_argument('-m','--max-read',  type=int,  default=1024,  help='maximum to read in kb [Default: %(default)s]')
parser.add_argument('-p','--max-points',  type=int,  default=50,  help='maximum data points to hold [Default: %(default)s]')
args = parser.parse_args()

inputFile = open("data.csv", mode = "r")
csv_reader = csv.reader(inputFile)
csv_pos = 0
fmt = "<" + ''.join( entry[0] for entry in datamap)
print(fmt)
def plot_figure(data):
    layout = dict(
        title="Figure w/ plotly",
        uirevision=1
    )

    fig = dict(data=data, layout=layout)
    return fig

app = dash.Dash()


app.layout = html.Div(children=[
                html.Div([
                    dcc.RadioItems(id='set-time',
                        value=5000,
                        options=[
                            {'label': 'Every second', 'value': 1000},
                            {'label': 'Every 5 seconds', 'value': 5000},
                            {'label': 'Off', 'value': 60*60*1000} # or just every hour
                        ]),
                        dcc.Checklist(
                            id='checklist',
                            options=[ { 'label' : 'on', 'value': 1} ],
                            values=[2]
                        ),
                        ]),
                html.H1("Plotly test with Live update",
                        style={"font-family": "Helvetica",
                               "border-bottom": "1px #000000 solid"}),
                html.Div(children='''
                    Dash: A web application framework for Python.
                '''),
                html.Div(dcc.Graph(id='plot',  style={'height': '80vh'}),style={'height': '100vh'}),
#                dcc.Slider(
#                    id='year-slider',
#                    min=df['year'].min(),
#                    max=df['year'].max(),
#                    value=df['year'].min(),
#                    marks={str(year): str(year) for year in df['year'].unique()}
#                ),

#                html.Div([dcc.Graph(id='plot2'),]),
        dcc.Interval(id='live-update', interval=interval, n_intervals=0),
    ],)

@app.callback(Output('live-update', 'interval'), [Input('set-time', 'value')])
def update_interval(value):
    return value

@app.callback(Output('plot', 'figure'), [Input('live-update', 'n_intervals')])
def gen_plot(n):
    print("gen_plot: ")
    global data

    read_data(data, csv_reader)
    toDelete =  len(data[0])-args.max_points
    if toDelete > 0:
        print("Delete %d points" % toDelete)
        for values in data:
            del values[toDelete:]

    print("Number of samples %d in %d traces" % (len(data[0]),  len(data)) )
    trace = []
    for index, values in enumerate(data):
    #            print("Group: %s" % data_description[index][1])
        if index > 0:
            #legendgroup='group2',
            if toDelete > 0:
                del data[index][toDelete:]
            if data_description[index][1] == "temps":
                trace += [ go.Scatter(x=data[0], y=data[index], yaxis='y2',  name=data_description[index][0], line=dict(width=1)) ]
            elif data_description[index][1] == "flow":
                trace += [ go.Scatter(x=data[0], y=data[index], name=data_description[index][0], line=dict(width=1)) ]


    layout = go.Layout(
        title="Heating at Home",
        uirevision=1,
        yaxis=dict(domain=[0, 0.50]),
        yaxis2=dict(domain=[0.50, 1]),
    )

#    fig   = plot_figure(trace)
    fig = dict(data=trace,  layout=layout)
#    fig = tools.make_subplots(rows=1, cols=2)
#    fig.append_trace(trace_temps, 1, 1)
#    fig.append_trace(trace_flow, 1, 2)
#    fig['layout'].update(height=600, width=800, title='Heating at Home', uirevision=1, yaxis=dict(domain=[0, 0.50]), yaxis2=dict(domain=[0.50, 1]))
    print("gen_plot end 1.1")
    return fig

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

def parse_data2(data):
    for n, x in enumerate(data):
        value = datamap[n][1](x)
#        print("Value: " + str(value))
        if isinstance(value, list):
            for i in value:
                #if i[0]:
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
            integer_list = [ int(value) for value in row[4:] ]
            packed_data = bytes(struct.pack( str(len(row) -4) + "B", *integer_list))
            parsed_data = list(parse_data2(struct.unpack(fmt, packed_data)))

            data[0] += [ row[0] ]
            for index, value in enumerate(parsed_data):
                data[index + 1] += [ value ]
        else:
            skipCount += 1

def skipIfToMuch(fileToSkip,  maximumInKb):
    maxDataToReadInitially = maximumInKb * 1024
    fileToSkip.seek(0, 2)
    newPosition = fileToSkip.tell() - maxDataToReadInitially
    if newPosition < 0:
        newPosition = 0
    fileToSkip.seek(newPosition)
    fileToSkip.readline()

# for date
data += [ [] ]
data_description +=  [ [ "date_time", "none" ] ]
for map_entry in datamap:
#        print("Value: " + str(value))
    if isinstance(map_entry[2], list):
        for index, description in enumerate(map_entry[3]):
            data += [ [] ]
            data_description += [ [ str(description), str(map_entry[4][index]) ] ]
    else:
        data += [ [] ]
        data_description +=  [ [ str(map_entry[3]), str(map_entry[4]) ] ]

skipIfToMuch(inputFile,  args.max_read)
read_data(data, csv_reader)
print("dash core component version: %s" % dcc.__version__)


app.run_server(host="0.0.0.0",debug=args.debug)
