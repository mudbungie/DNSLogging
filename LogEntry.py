# This does cleanup on the database. It takes the messy rsyslog data, and goes through a couple of steps. 
# First, it scrubs out anything not from a DNS server, and builds Log objects out of everything else.
# Then, regex on that for a little bit, to make it into better data.
# Pull the necessary records from other databases and the like.
# Write the data back into the database in a more usable format.

#from Host import Host
import dateparser
from datetime import datetime

class NotADNSRecord(Exception):
    pass

class FileLogEntry:
    def __init__(self, record):
        # Takes a record written to a log file, parses it, records relevant DNS
        # info to a database object

        # Break the log into a space delimited list; all interactions from
        # here on out will be on the segments
        self.record = record.split()
        # Make sure that it's from the right daemon
        if self.isGoodLog():
            self.parse()
        else:
            # Raise an exception, because we want to toss this log 
            raise NotADNSRecord(record)

    def parse(self):
        # Cut the record into pieces, commit them to a dictionary
        self.values = {}
        self.values['querytime'] = dateparser.parse(str(self.record[0:3]))
        self.values['reporttime'] = datetime.now()
        self.values['answeringserver'] = self.record[3]
        self.values['client_ip'] = self.record[7]
        self.values['request'] = self.record[8]
        self.values['type'] = self.record[9]

        # diagnostic
        #for key, value in self.values.items():
        #    print(key + ' ' + str(value))
        return True
    def isGoodLog(self):
        # Presently, we're just going for DNS records
        permissibleLogTypes = ['unbound:']
        if self.record[4] in permissibleLogTypes:
            return True
        else:
            return False
    def commit(self, database):
        # Commit the parsed record to the database
        database.insertDNSRecord(self.values)

    def getMac(self, database):
        # Query the ARP records for the MAC address
        mac = database.getMac(self.values['client_ip'], self.values['querytime'])
        self.values['client_mac'] = mac

    def getCustNum(self, radiusDict):
        # If possible, get the custid from the RADIUS data
        try:
            self.values['custnum'] = radiusDict[self.values['client_mac']]
        except KeyError:
            # If it's not there, it's not there
            self.values['custnum'] = None

