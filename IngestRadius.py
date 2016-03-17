# Okay, so fuck that I had to write this
# Anyhow, queries to the RADIUS database are literally taking over a second.
# Which, given that we're running at over 100 queries/second, is unacceptable.
# Normally, the solution would be to use a materialized view, but I have no
# idea how to do that across different database engines (mariadb/postgres)
# So, what the fuck ever. It's a database, not a baby. Just make it do the 
# things you want.

# This just runs a single query against the RADIUS database, and ingests all
# that data into the local postgres database, where I can run timely queries.

import Database
from Config import config

class RadiusDatabase(Database):
    def cloneTable(self, remoteDB):
        # Go through the records from either database. 
        sourceTable = remoteDB.initTable('username_mac')
        destTable = self.initTable('radius')
        # Hitting the remote database has huge latency, so just do it once
        # and get everything.
        remoteRecords


if __name__ == '__main__':
    # We take records from the remote, and clone them to the local
    remotedb = RadiusDatabase(config['databases']['radius'])
    localdb = RadiusDatabase(config['databases']['dnslog'])
