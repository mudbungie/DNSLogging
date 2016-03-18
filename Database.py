# Definition for the database itself

# DB adapter
#import psycopg2
import sqlalchemy as sqla
# Objects that handle the internal logic of each request
from LogEntry import FileLogEntry
import datetime

class Database:
    def __init__(self, databaseConfig):
        # Open the database with the info in the config
        self.dbname = databaseConfig['dbname']
        self.dbtype = databaseConfig['dbtype']
        self.host = databaseConfig['host']
        self.user = databaseConfig['user']
        self.password = databaseConfig['password']
        self.connect()

    def connect(self):
        # Construct a string out of all of this data
        if self.dbtype == 'postgresql':
            prefix = 'postgresql+psycopg2://'
        elif self.dbtype == 'mysql':
            prefix = 'mysql+pymysql://'
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
            return None

    def getCustNum(self, mac):
        #FIXME This is deprecated; would work fine, but the IO latency on that
        # database is extreme, so user getRadiusData instead

        # When connected to the RADIUS database, returns a freeside custnum
        tableName = 'username_mac'
        #radRecords = self.metadata.tables[tableName]
        radRecords = sqla.Table(tableName, self.metadata, autoload=True, 
            autoload_with=self.connection)

        # Have to start by formatting the MAC address, because freeside records it differently
        fmac = mac.replace(':', '-').upper()
        # Get the matching record from RADIUS
        radQuery = radRecords.select().where(radRecords.c.Name_exp_2 == fmac)
        radRecord = self.connection.execute(radQuery)

        # Make sure that the data isn't funky
        assert radRecord.rowcount <= 1

        try:
            # If there are no hits, this will throw an error
            radUsername = radRecord.fetchone().username
            username = ''.join(c for c in radUsername if c.isdigit())
        except AttributeError:
            # But that's fine, some authenticated devices don't have usernames
            username = None
        # The are serial numbers that sometimes have extra alpha characters.
        # We don't want those alpha characters, because they don't associate
        # Scrub everything but digits
        return username

    def getRadiusData(self):
        # Pulls RADIUS associations of MACs to clientids
        radTable = sqla.Table('username_mac', self.metadata, autoload=True,
            autoload_with=self.connection)
        radQuery = radTable.select()
        radRecords = self.connection.execute(radQuery)

        radData = {}
        for radRecord in radRecords:
            # Make sure that it's actually a custid, this table is dirty
                if radRecord.username[0].isdigit():
                    # Reformat the MAC address 
                    # One day I'll find out why the RADIUS column names are so weird
                    usableMac = radRecord.Name_exp_2.replace('-', ':').lower()
                    # Scrub alpha characters from the username
                    custid = ''.join(c for c in radRecord.username if c.isdigit())
                    radData[usableMac] = custid
        return radData

    def initTable(self, tableName):
        # Didn't realize that I'd end up doing this so many times
        #FIXME Go through and make everything use this function instead
        table = self.metadata.tables[tableName]
        return table

    def getCustByName(self, name):
        print(name)
        custTable = self.initTable('cust_main')
        
        # We might search by the billing name or the company name
        billingOrCompany = sqla.or_(custTable.c.payname.like(name), 
            custTable.c.company.like(name))
        # We also might search by first and last name, which is two fields
        try:
            names = name.split()
            firstName = names[0]
            lastName = names[-1]
        except KeyError:
            # Means that a request was given with no space;
            lastName = names[0]
        firstAndLast = sqla.and_(custTable.c.first == firstName, custTable.c.last == lastName)
        # Combine them
        nameOrBillingOrCompany = sqla.or_(billingOrCompany, firstAndLast)
        custsByName = custTable.select().where(nameOrBillingOrCompany)
        custs = self.connection.execute(custsByName)
        return custs

    def getRecordsByIP(self, ip):
        dnslogTable = self.initTable('dnslog')
        query = dnslogTable.select().where(dnslogTable.c.client_ip == ip).\
            order_by(dnslogTable.c.querytime.desc())
        records = self.connection.execute(query)
        return records

    def getRecordsByCustnum(self, custnum):
        dnslogTable = self.initTable('dnslog')
        query = dnslogTable.select().where(dnslogTable.c.custnum == custnum).\
            order_by(dnslogTable.c.querytime.desc())
        records = self.connection.execute(query)
        return records

