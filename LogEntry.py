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
        self.values['client'] = self.record[7]
        self.values['request'] = self.record[8]
        self.values['type'] = self.record[9]

        # diagnostic
        for key, value in self.values.items():
            print(key + ' ' + str(value))
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
        database.insertLog(self.values)


# For DB records, which have been inserted into a database already
# Isn't working on the production machine, because OpenBSD is funky, but
# works fine on my own machines, so I'm not about to scrap it.
class DBLogEntry:
    def __init__(self, record, database):
        # Takes a record from postgres, and the working DB
        # Throws out inappropriate logs, chews on the data
        # Throws it into another table, and purges the old

        # Needs to refer back to the originating DB
        self.database = database
        
        # Clean it up, record instance attributes
        # The record comes back as a list, so make dict meaningful values
        self.values = {}
        self.values['id'] = record[0]
        print(self.values['id'])
        self.values['logtype'] = record[20]
        
        # Make sure that it's from a DNS server
        permissibleLogTypes = ['unbound:']
        if not self.values['logtype'] in permissibleLogTypes:
            print('Log with id ' + str(self.values['id']) + ' unsupported.')
            self.purgeLog()
            return None
        else:
            pass
            #print(self.values['logtype'])

        # Back to encoding values
        self.values['timestamp'] = record[2]
        self.values['dns_server'] = record[6]
        
        # Message has the meat of the data, so parse it
        self.values['message'] = record[7]
        try:
            self.parseMessage()
        except:
            print(record)
            raise

        #self.getHostValues()        
        self.saveRecord()
        self.purgeLog()

    def parseMessage(self):
        # Split the record fields on spaces
        message = self.values['message'].split()
        self.values['client_ip'] = message[2]
        self.values['requested_name'] = message[3]
        self.values['type'] = message[4]
        #print(self.values['id'], self.values['client'], self.values['logtype'])

    #def getHostValues(self):
    #    # Initialize a Host object, pull relevant values out of it
    #    host = Host(self.values['client'])
    #    self.values['MAC'] = host.mac
    #    self.values['userid'] = host.userid
    #    print(self.values['MAC'])
    #    print(self.values['userid'])

    def purgeLog(self):
        # Remove log from the syslog ingress table
        #print('Deleting log entry with id ' + str(self.values['id']))
        self.database.deleteLogById(self.values['id'])

    def constructInsert(self):
        # Constructs an INSERT statement based on the attributes of the object
        # returns string.
        structure = 'INSERT INTO dnslog (client, requested_name, timestamp, server, type) VALUES ('
        valueString = ', '.join([
                                self.values['client'], 
                                self.values['name'], 
                                self.values['timestamp'], 
                                self.values['dnsserver'], 
                                self.values['type'],
                                ])
        insert = structure + valueString
        return insert
    def saveRecord(self):
        # Writes the query back to the database all cleaned up, and in a new format
        #print('recording')
        self.database.insertIntoTable(self.values, 'dnslog')
        
