#!/usr/local/bin/python3

# This is a little webserver. Its purpose is to provide the same data as the
# CheckDNSwhatever command line system.

import bottle

# The index page, just returns a document.
@bottle.route('/')
def index():
    with open('index.html', 'r') as indexhtml:
        return indexhtml.read()

bottle.run(host='127.0.0.1', port=6000)
