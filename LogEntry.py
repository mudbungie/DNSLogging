# This does cleanup on the database. It takes the messy rsyslog data, and goes through a couple of steps. 
# First, it scrubs out anything not from a DNS server, and builds Log objects out of everything else.
# Then, regex on that for a little bit, to make it into better data.
# Pull the necessary records from other databases and the like.
# Write the data back into the database in a more usable format.

# DB adapter
import psycopg2
# Configuration
from Config import config

class LogEntry:
    def __init__(self, record, database):
        # Takes a record from postgres
        self.database = database
        
        # Clean it up, record instance attributes
        # The record comes back as a list, so make dict meaningful values
        self.values = {}
        self.values['id'] = record[0]
        self.values['date'] = record[2]
        self.values['dnsserver'] = record[6]
        self.values['message'] = record[7] # This needs parsing
        self.values['logtype'] = record[20]
        #print(self.values['message'])
        self.parseMessage()

    def parseMessage(self):
        # Split the record fields on spaces
        message = self.values['message'].split()
        self.values['client'] = message[2]
        self.values['name'] = message[3]
        self.values['type'] = message[4]
        print(self.values['client'])

    def logCleaning(self):
        # Reasons to purge the log
        
        # It's not from a dns server
        permissibleLogTypes = ['unbound:']
        if not self.values['logType'] in permissibleLogTypes:
            print('Log with id ' + str(self.values['id']) + ' unsupported.')
            self.purgeLog

    def purgeLog(self):
        # Remove log from the syslog ingress table
        print('Deleting log entry with id ' + self.values['id'])
        self.database.deleteLogById(self.values['id'])

    def constructInsert(self):
        # Constructs an INSERT statement based on the attributes of the object
        # returns string.
        pass
    def recordQuery(self):
        # Writes the query back to the database all cleaned up, and in a new format
        pass
        
class Database:
    def __init__(self, databaseConfig):
        # Open the database with the info in the config
        self.dbname = databaseConfig['dbname']
        self.host = databaseConfig['host']
        self.user = databaseConfig['user']
        self.password = databaseConfig['password']
        self.connect()

    def connect(self):
        # Construct a string out of all of this data
        connectionString = ' '.join([   'dbname=' + self.dbname, 
                                        'user=' + self.user,
                                        'password=' + self.password, 
                                        'host=' + self.host,
                                        ])
        self.connection = psycopg2.connect(connectionString)

    def getSyslogRecords(self, count=10):
        cursor = self.connection.cursor()
        queryString = 'SELECT * FROM systemevents'
        cursor.execute(queryString)
        records = cursor.fetchmany(count)
        for record in records:
            logEntry = LogEntry(record, self)
        cursor.close()

    def deleteLogById(self, logid):
        cursor = self.connection.cursor()
        #queryString = 'DELETE FROM systemevents WHERE id=' + str(logid)
        cursor.close()

if __name__ == '__main__':
    a = Database(config['databases']['syslog'])
    a.connect()
    a.getSyslogRecords()
