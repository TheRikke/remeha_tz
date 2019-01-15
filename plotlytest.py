#!/usr/bin/python

import dash
import pandas as pd
import plotly.graph_objs as go 
import dash.dependencies as ddp
import dash_core_components as dcc
import dash_html_components as html
import string
from dash.dependencies import Input, Output

alphabet =  list(string.ascii_lowercase)
second = 1000
minute = 60
hour   = 60
day    = 24
interval = 5000

ind = [0, 0.1, 0.2, 0.3]
df = pd.DataFrame({'one' : pd.Series([4., 3., 2., 1.], index=ind),
                   'two' : pd.Series([1., 2., 3., 4.], index=ind)})
indexvalue = 0.3
counter = 0

inputFile = open("test.bin", mode = "rb")


def plot_figure(data):
    layout = dict(
        title="Figure w/ plotly",
    )

    fig = dict(data=data, layout=layout)
    return fig

def gen_plot(dopboxvalue):
    print dopboxvalue
    global counter
    global df
    global indexvalue
    
    data = inputFile.read(2)
    while len(data) > 0:
        indexvalue = indexvalue + 0.1
        df.loc[ indexvalue ] = [ counter, indexvalue ]
        counter = counter + 1
        data = inputFile.read(2)
    #print alphabet[indexvalue]
    #df = df.append({'one': counter}, ignore_index=True)
    #df = df.append({'two': ind}, ignore_index=True)
    #df.loc[ indexvalue ] = [ counter, indexvalue ]
    if dopboxvalue is None or dopboxvalue:
        trace = [go.Scatter(x=df.index, y=df['one']), go.Scatter(x=df.index, y=df['two'])]
        fig   = plot_figure(trace)
        print "update"
        return fig
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
                    values=[1]
                ),
                html.H1("Plotly test with Live update",
                        style={"font-family": "Helvetica", 
                               "border-bottom": "1px #000000 solid"}),
                ], className='banner'),
        html.Div([dcc.Graph(id='plot', figure=gen_plot(1))],),
        dcc.Interval(id='live-update', interval=interval),
    ],)

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

if __name__ == '__main__':
    app.run_server(debug=True)
