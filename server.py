#!/usr/local/bin/python3

# This is a little webserver. Its purpose is to provide the same data as the
# CheckDNSwhatever command line system.

import bottle
from CheckDNSRecords import getWebTable
import TimeStamps
logInterface = bottle.Bottle()

# The index page, just returns a document.
@logInterface.route('/')
def index():
    with open('index.html', 'r') as indexhtml:
        return indexhtml.read()

@logInterface.post('/query')
def answerQuery():
    # There is a form with datetime for the beginning and end of the search
    # period. Extract that data,
    query = bottle.request.forms.get('searchString')
    dstart = bottle.request.forms.get('dstart')
    tstart = bottle.request.forms.get('tstart')
    dstop = bottle.request.forms.get('dstop')
    tstop = bottle.request.forms.get('tstop')
    # Then convert it out of the strings that you get from the web
    start = TimeStamps.convertDate(dstart, tstart)
    stop = TimeStamps.convertDate(dstop, tstop)
    # Pass that and the actual query string to the database and formatter
    return getWebTable(query, start, stop)

@logInterface.route('/favicon.ico')
def fuckyou():
    return None

logInterface.run(host='127.0.0.1', port=6000)
