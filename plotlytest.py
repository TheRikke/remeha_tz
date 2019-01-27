#!/usr/bin/python

import dash
#import pandas as pd
import plotly.graph_objs as go 
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as html
import string
import csv
import struct
from dash.dependencies import Input, Output
from datamap import datamap, fmt
from datetime import datetime,timedelta,date
import dateutil.parser
alphabet =  list(string.ascii_lowercase)
second = 1000
minute = 60
hour   = 60
day    = 24
interval = 5000

ind = [0, 0.1, 0.2, 0.3]
#df = pd.DataFrame({'one' : pd.Series([4., 3., 2., 1.], index=ind),
#                   'two' : pd.Series([1., 2., 3., 4.], index=ind)})

data_dates = []
data_vorlauf = []
data_ruecklauf = []
data_powerlevel = []
indexvalue = 0.3
counter = 0

inputFile = open("data.csv", mode = "r")
csv_reader = csv.reader(inputFile)
csv_pos = 0

def plot_figure(data):
    layout = dict(
        title="Figure w/ plotly",
    )

    fig = dict(data=data, layout=layout)
    return fig

def gen_plot(dopboxvalue):
    print("gen_plot: " + str(dopboxvalue))
    global counter
    global df
    global indexvalue
    global data_dates
    global data_vorlauf
    global data_ruecklauf
    global data_powerlevel
#    data = inputFile.read(2)
#    while len(data) > 0:
#        indexvalue = indexvalue + 0.1
#        df.loc[ indexvalue ] = [ counter, indexvalue ]
#        counter = counter + 1
#        data = inputFile.read(2)
    firstValidDateFound = True
    errorCount = 0
    skipCount = 0
    readCount = 0
    DateAndTimeToParse = None
    for row in csv_reader:
        readCount += 1
        #strrow = ','.join(str(e) for e in row)
#        print("Row[2]: " + str(row[2]))
#        print(len(row))
        try:
            if not firstValidDateFound and dateutil.parser.parse(row[0]) >= DateAndTimeToParse:
                firstValidDateFound = True
        except:
            errorCount += 1
            continue
        if firstValidDateFound:
            if row[2] == "258" and len(row) >= 68:
                data_dates += [ row[0] ]
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
                data_vorlauf += [ parsed_data[0][1] ]
                data_ruecklauf += [ parsed_data[1][1] ]
                data_powerlevel += [ parsed_data[19][1] ]

    #            print("parsed_data[0]: " + str(parsed_data[0]))
    #            strrow1 = ','.join(str(e) for e in data_dates)
    #            strrow2 = ','.join(str(e) for e in data_vorlauf)
    #            print("Dates:" + strrow1)
    #            print("Vorlauf: " + strrow2)
        else:
            skipCount += 1
    print("Update Values: %s, readCount %d, skipped %d, errors %d" % (len(data_dates), readCount, skipCount, errorCount))


    if dopboxvalue is None or dopboxvalue:
 #       strrow1 = ','.join(str(e) for e in data_dates)
 #       strrow2 = ','.join(str(e) for e in data_vorlauf)

 #       print("Dates:" + strrow1)
 #       print("Vorlauf: " + strrow2)
        trace = [go.Scatter(x=data_dates, y=data_vorlauf, name="Vorlauf"),
                 go.Scatter(x=data_dates, y=data_ruecklauf, name="Rücklauf"),
                 go.Scatter(x=data_dates, y=data_powerlevel, name="PowerLevel")
                 ]
        fig   = plot_figure(trace)
        print("gen_plot end")
        return fig
    print("gen_plot end 2 ")
    return None

def serve_layout():
    return html.Div(children=[
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
                html.H1("Plotly test with Live update",
                        style={"font-family": "Helvetica", 
                               "border-bottom": "1px #000000 solid"}),
                ], className='banner'),
        html.Div([dcc.Graph(id='plot', figure=gen_plot(1))],),
        dcc.Interval(id='live-update', interval=interval),
    ],)

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

#if __name__ == '__main__':
#    df = pd.read_csv(inputFile, parse_dates=True)
DateAndTimeToParse = datetime.now() - timedelta(hours=1)
firstValidDateFound = False
errorCount = 0
skipCount = 0
readCount = 0
for row in csv_reader:
    readCount += 1
    #strrow = ','.join(str(e) for e in row)
#        print("Row[2]: " + str(row[2]))
#        print(len(row))
    try:
        if not firstValidDateFound and dateutil.parser.parse(row[0]) >= DateAndTimeToParse:
            firstValidDateFound = True
    except:
        errorCount += 1
        continue
    if firstValidDateFound:
        if row[2] == "258" and len(row) >= 68:
            data_dates += [ row[0] ]
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
            data_vorlauf += [ parsed_data[0][1] ]
            data_ruecklauf += [ parsed_data[1][1] ]
            data_powerlevel += [ parsed_data[19][1] ]

#            print("parsed_data[0]: " + str(parsed_data[0]))
#            strrow1 = ','.join(str(e) for e in data_dates)
#            strrow2 = ','.join(str(e) for e in data_vorlauf)
#            print("Dates:" + strrow1)
#            print("Vorlauf: " + strrow2)
    else:
        skipCount += 1

#csv_pos = inputFile.
print("Values: %s, read %d, skipped %d, errors %d" % (len(data_dates), readCount, skipCount, errorCount))

app = dash.Dash()
app.layout = serve_layout

@app.callback(
    dash.dependencies.Output('live-update', 'interval'),
    [dash.dependencies.Input('set-time', 'value')])
def update_interval(value):
    return value

app.callback(
    ddp.Output('plot', 'figure'),
    [Input('checklist', 'values')],
    [],
    [ddp.Event('live-update', 'interval')])(gen_plot)

app.run_server(host="0.0.0.0",debug=True)
