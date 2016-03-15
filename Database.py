# Definition for the database itself

# DB adapter
#import psycopg2
import sqlalchemy as sqla
# Objects that handle the internal logic of each request
from LogEntry import FileLogEntry

class Database:
    def __init__(self, databaseConfig):
        # Open the database with the info in the config
        self.dbname = databaseConfig['dbname']
        self.dbtype = datebaseConfig['dbtype']
        self.host = databaseConfig['host']
        self.user = databaseConfig['user']
        self.password = databaseConfig['password']
        self.connect()

    def connect(self):
        # Construct a string out of all of this data
        if self.dbtype == 'postgresql':
            prefix = 'postgresql+psycopg2://'
        elif self.dbtype == 'mysql':
            prefix = 'mysql://'
        connectionString = ''.join([    prefix,
                                        self.user, ':',
                                        self.password, '@',
                                        self.host, '/',
                                        self.dbname, 
                                        ])
        self.connection = sqla.create_engine(connectionString)
        self.metadata = sqla.MetaData(self.connection)
        self.metadata.reflect()

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
            #print(data[justTheName], len(values))
            try:
                values[justTheName.lower()] = data[justTheName.lower()]
                #print("MATCH!")
            except KeyError:
                pass
        if len(values) == 0:
            print('nothing matched, something\'s wrong.')
            raise Exception('nope')

        # This is the SQL that will be executed
        insert = table.insert().values(**values)
        # Do it
        pkey = self.connection.execute(insert).inserted_primary_key
        return pkey 

    def insertDNSRecord(self, data):
        # Just a simple helper mask, so log objects don't need to know
        # table structure.
        self.insertIntoTable(data, 'dnslog')
       
    def getMac(self, ip, time):
        # Find what MAC address owned a certain IP at a certain time

        # Connect to the ARP records collected from our routers
        tableName = 'arp'
        arpRecords = self.metadata.tables[tableName]

        # Records about that IP address that are at the correct time
        unexpired = sqla.or_(arpRecords.c.expired == None, arpRecords.c.expired > time)
        correctTime = sqla.and_(arpRecords.c.observed < time, unexpired)
        matchingArpQuery = sqla.and_(arpRecords.c.ip == ip, correctTime)

        matchingRecordSelect = arpRecords.select().where(matchingArpQuery)

        matchingRecords = self.connection.execute(matchingRecordSelect)
        # There should only be one record, or something is wrong
        #print(ip)
        #print(time)
        #print(matchingArpQuery)
        #print(matchingRecords.rowcount)
        assert matchingRecords.rowcount <= 1
        # Answer with the MAC
        try:
            return matchingRecords.fetchone().mac
        except:
            return False

    def getCustNum(self, mac):
        # When connected to the RADIUS database, returns a freeside custnum
        tableName = 'username_mac'
        radRecords = self.metadata.tables[tableName]

        # Have to start by formatting the MAC address, because freeside records it differently
        fmac = mac.replace(':', '-').upper()
        # Get the matching record from RADIUS
        radQuery = radRecords.select().where(radRecords.c.name_exp_2 == fmac)
        radRecord = self.connection.execute(radQuery)

        # Make sure that the data isn't funky
        assert radRecord.rowcount <= 1

        # The are serial numbers that sometimes have extra alpha characters.
        # We don't want those alpha characters.
        radUsername = radRecord.fetchone().username
        # Scrub everything but digits
        username = ''.join(c for c in radUsername if c.isdigit())
        return username
