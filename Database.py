# Definition for the database itself

# DB adapter
import psycopg2
# Objects that handle the internal logic of each request
from LogEntry import LogEntry
# Config
from Config import config

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

    def getRecordsFromTable(self, table, count=1000):
        cursor = self.connection.cursor()
        queryString = 'SELECT * FROM ' + table + ' limit ' + str(count)
        cursor.execute(queryString)
        records = cursor.fetchmany(count)
        cursor.close()
        return records

    def getSyslogRecords(self, count=1000):
        #cursor = self.connection.cursor()
        #queryString = 'SELECT * FROM systemevents limit ' + str(count)
        #cursor.execute(queryString)
        #records = cursor.fetchmany(count)
        records = self.getRecordsFromTable('systemevents')
        # Replace the list items with more useful versions of themselves
        for record in records:
            # The item initialization handles all the things that we need to do
            record = LogEntry(record, self)
        #cursor.close()

    def deleteLogById(self, logid):
        cursor = self.connection.cursor()
        queryString = 'DELETE FROM systemevents WHERE id=' + str(logid)
        cursor.execute(queryString)
        #print(cursor.statusmessage)
        self.connection.commit()
        cursor.close()

    def insertIntoTable(self, values, table):
        # Takes a dict of values, matches keys to column name, returns a string
        #FIXME This should be dynamic to the column names
        #print('inserting')
        cursor = self.connection.cursor()
        insert = cursor.mogrify('INSERT INTO ' + table + '(client, requested_name, ' + 
                        'timestamp, server, type) VALUES (%s, %s, %s, %s, %s)',
                                (values['client'],
                                values['requested_name'],
                                values['date'],
                                values['dnsserver'],
                                values['type'],)
                        )
        cursor.execute(insert)
        self.connection.commit()
        cursor.close()

    def insertDNSLog(self, insert):
        cursor = self.connection.cursor()
        cursor.execute

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    a = Database(config['databases']['syslog'])
    a.connect()
    a.getSyslogRecords()
    a.close()
