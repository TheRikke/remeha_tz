# Boiler Logger for Remeha Tzerra

## Features

This logger is meant to read data from a Remeha Boiler and distribute it to different backends.
Currently it only supports reading from a ***Remeha Tzerra*** and writing to a ***MQTT broker***, a
***CSV file***, and/or ***MySQL/MariaDB***. It should be easy to add support for other Remeha Boilers.

There is an additional Python Script (plotlytest.py) which can read the csv file written by the
logger and render some nice diagrams. As the name suggests it uses Plotly to do interactive
diagrams and dash to distribute it with a simple webservice.

## Installing

You need ***Python 3*** installed. There is a setup.py provided, which you could call directly or
even better use "pip" to install:

For the latest released version:

```
pip install remeha-tz
```

or for the latest version on github:

```
pip install git+https://github.com/TheRikke/remeha_tz.git@master
```

If you want to log to a mysql/mariadb, please copy config/remeha.conf to ~/remeha.conf, ~/.remeha.conf or /etc/remeha/remeha.conf
and change the database parameter in there.

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

https://en.wikipedia.org/wiki/Modular_connector#4P4C

Connect the number pins of the 4P4C connector to the following pins of your board or TTL-USB converter:

* pin 1 - GND
* pin 2 - TX
* pin 3 - RX
* pin 4 - VCC 5 (I did not connect this one. Just for reference.)

