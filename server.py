#!/usr/local/bin/python3

# This is a little webserver. Its purpose is to provide the same data as the
# CheckDNSwhatever command line system.

import bottle
from CheckDNSRecords import getWebTable

logInterface = bottle.Bottle()

# The index page, just returns a document.
@logInterface.route('/')
def index():
    with open('index.html', 'r') as indexhtml:
        return indexhtml.read()

@logInterface.post('/query')
def answerQuery():
    query = bottle.request.forms.get('query')
    return getWebTable(query)

logInterface.run(host='127.0.0.1', port=6000)
