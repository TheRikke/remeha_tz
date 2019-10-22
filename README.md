# Boiler Logger for Remeha Tzerra

## Features

This logger is meant to read data from a Remeha Boiler and distribute it to different backends.
Currently it only supports reading from a ***Remeha Tzerra*** and writing to a ***MQTT broker*** or a
***CSV file***. It should be easy to add support for other Remeha Boilers.

There is an additional Python Script (plotlytest.py) which can read the csv file written by the
logger and render some nice diagrams. As the name suggests it uses Plotly to do interactive
diagrams and dash to distribute it with a simple webservice.

## Installing

You need ***Python 3*** installed. There is a setup.py provided, which you could call directly or
even better use "pip" to install:

```
pip install <path to remeha_tz repository>
```

If you don't need the plotly diagrams, You can remove the 'dash' and 'plotly' dependencies from
setup.py.
## Usage

```
remeha.py -d /dev/ttyUSB0 --output test.csv
```

This will start logging to the local mqtt broker with the topic 'boiler/' and the specified csv
file. See ```--help``` for more options.

## Other useful information

The csv file contains the raw frame received from the boiler and not the decoded values. This
is done because I'm not sure about the meaning of some of the values. By saving the raw frame
we don't loose any data and are able to decode them later. Also it makes supporting other
boiler types more easy.

To convert the csv with raw values to csv with decoded values use the convert script:

```
remeha_convert.py --input-file <data csv> > converted.csv
```

## Hardware

Most Remeha boiler use a simple serial connection with 5V TTL. If you have a Raspberry Pi, Arduino or similar, 
it can most likely be directly connected to the boiler. To connect it to 3.3V like a PC you need a TTL converter or 
a TTL-USB converter. 
The remeha tzerra uses a RJ10 aka. 4P4C connector. I've used a old phone cord to connect my Raspberry Pi clone to the
boiler.
