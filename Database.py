# Definition for the database itself

# DB adapter
#import psycopg2
import sqlalchemy as sqla
# Objects that handle the internal logic of each request
from LogEntry import LogEntry
# Configuration stored in a gitignored file
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
        connectionString = ''.join([    'postgresql+psycopg2://',
                                        self.user, ':',
                                        self.password, '@',
                                        self.host, '/',
                                        self.dbname, 
                                        ])
        self.connection = sqla.create_engine(connectionString)
        self.metadata = sqla.MetaData(self.connection)

    def getRecordsFromTable(self, tableName, count=100):
        # Returns an object that already has the schema mapped
        # Initialize table object
        table = sqla.Table(tableName, self.metadata, autoload=True)
        # Construct the relevant query
        select = sqla.select([table]).limit(count)
        # Run it
        records = self.connection.execute(select)

        return records

    def getSyslogRecords(self, count=100):
        records = self.getRecordsFromTable('systemevents')
        # Replace the list items with more useful versions of themselves
        for record in records:
            # The item initialization handles all the things that we need to do
            record = LogEntry(record, self)

    def deleteLogById(self, logId):
        table = sqla.Table('systemevents', self.metadata, autoload=True)
        delete = table.delete(table.c.id == logId)
        self.connection.execute(delete)

    def insertIntoTable(self, data, tableName):
        # Gets a dict of values, inserts them into like-named fields in the DB
        table = sqla.Table(tableName, self.metadata, autoload=True)

        # Go through all the fields in the table, see which of them apply
        values = {}
        for column in table.columns:
            # That attribute is fully qualified, which isn't what I want
            justTheName = str(column).split('.')[1]
            #print(justTheName)
            try:
                values[justTheName] = data[justTheName]
            except KeyError:
                pass

        # This is the SQL that will be executed
        insert = table.insert().values(**values)
        # Do it
        self.connection.execute(insert)

if __name__ == '__main__':
    a = Database(config['databases']['syslog'])
    a.getSyslogRecords()
