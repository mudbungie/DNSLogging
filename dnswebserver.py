#!/usr/local/bin/python3

# This is a little webserver. Its purpose is to provide the same data as the
# CheckDNSwhatever command line system.

import bottle
from CheckDNSRecords import getWebTable
from WebInterface import getUserProfiles, getCustJson
import TimeStamps
import cProfile, pstats, io
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
    print('start', start)
    print('stop', stop)
    # Pass that and the actual query string to the database and formatter
    return getWebTable(query, start, stop)

@logInterface.route('/custs.json')
def custsJson():
    #pr = cProfile.Profile()
    #pr.enable()
    #a = getCustJson()
    #pr.disable()
    #s = io.StringIO()
    #sortby = 'cumulative'
    #ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    #ps.print_stats()
    #print(s.getvalue())
    #return a
    return getCustJson()

@logInterface.route('/userProfiles')
def userProfiles():
    # Return a big JSON blob for use in the autocomplete function
    return getUserProfiles()

@logInterface.route('/favicon.ico')
def fuckyou():
    return None

logInterface.run(host='127.0.0.1', port=6000)
