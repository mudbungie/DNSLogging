# Definition for the database itself

# DB adapter
import sqlalchemy as sqla
# Objects that handle the internal logic of each request
from LogEntry import FileLogEntry
import datetime

class Database:
    def __init__(self, databaseConfig):
        self.initDB(databaseConfig)
        # Defined in child classes, pertains to tables they use
        self.initTables()

    def initDB(self, databaseConfig, reflect=True):
        # Open the database with the info in the config
        self.dbname = databaseConfig['dbname']
        self.dbtype = databaseConfig['dbtype']
        self.host = databaseConfig['host']
        self.user = databaseConfig['user']
        self.password = databaseConfig['password']
        self.reflect = reflect
        self.connect()
    
    def connect(self, reflect=True):
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
        if self.reflect:
            self.metadata.reflect()

    def initTable(self, tableName):
        # Didn't realize that I'd end up doing this so many times
        # This method is more temperamental to permissions
        #table = self.metadata.tables[tableName]
        # so I'm using this instead.
        table = sqla.Table(tableName, self.metadata, autoload=True, 
            autoload_with=self.connection)
        return table

    def initTables(self, tableNames):
        # Take a list of tables, assign an attribute which is a dict of the
        # initialized tables, so that they don't need to be reopened later.
        self.tables = {}
        for tableName in tableNames:
            self.tables[tableName] = self.initTable(tableName)

    def insertIntoTable(self, data, table):
        # Gets a dict of values, inserts them into like-named fields in the DB

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
            # Make sure you're inserting something at all
            print('nothing matched, something\'s wrong.')
            raise Exception('empty insert, probable table-value mismatch')

        # This is the SQL that will be executed
        insert = table.insert().values(**values)
        # Do it
        pkey = self.connection.execute(insert).inserted_primary_key
        return pkey 

    def getCustNum(self, mac):
        #FIXME This is deprecated; would work fine, but the IO latency on that
        # database is extreme, so use getRadiusData instead

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

