# Database subclass for handling the dnslog database.

from Database import Database
import sqlalchemy as sqla

class DNSLogDB(Database):
    def __init__(self, databaseConfig):
        self.initDB(databaseConfig)
        tables = ['dnslog', 'arp']
        self.initTables(tables)
        self.getMacs()

    def insertDNSRecord(self, data):
        # Simple helper mask, so that log objects don't need to know table 
        # structure.
        self.insertIntoTable(data, self.tables['dnslog'])

    def getMacs(self):
        # I spend a lot of time querying for MAC addresses, so I'm going to
        # cache the table for performance reasons.
        arpRecords = self.tables['arp']
        arpQuery = arpRecords.select().where(arpRecords.c.expired == None)
        arpRecords = self.connection.execute(arpQuery)

        self.mac = {}
        for arpRecord in arpRecords:
            self.mac[arpRecord.ip] = arpRecord.mac

    def getMac(self, ip, time):
        # Just look in the local dict. Since I'm shorthanding the table, 
        # there's no expiry check.
        try:
            mac = self.mac[ip]
        except:
            mac = None
        return mac
    '''
    def getMac(self, ip, time):
        # Find what MAC address owned a certain IP at a certain time

        # Connect to the ARP records collected from our routers
        arpRecords = self.tables['arp']

        # Records about that IP address that are at the correct time
        unexpired = sqla.or_(arpRecords.c.expired == None, arpRecords.c.expired > time)
        correctTime = sqla.and_(arpRecords.c.observed < time, unexpired)
        matchingArpQuery = sqla.and_(arpRecords.c.ip == ip, correctTime)

        matchingRecordSelect = arpRecords.select().where(matchingArpQuery)

        matchingRecords = self.connection.execute(matchingRecordSelect)
        # There should only be one record, or something is wrong
        assert matchingRecords.rowcount <= 1
        # Answer with the MAC
        try:
            return matchingRecords.fetchone().mac
        except:
            return None
    '''
    def getCustRecords(self, table, whereclause):
        # Get records according to some where clause
        query = table.select().where(whereclause).order_by(table.c.querytime.desc())
        records = self.connection.execute(query)
        return records

    def getRecordsByIP(self, ip):
        table = self.tables['dnslog']
        where = table.select().where(table.c.client_ip == ip).order_by(table.c.querytime.desc())
        return self.connection.execute(where)

    def getRecordsByCustnum(self, custnum):
        table = self.tables['dnslog']
        where = table.select().where(table.c.custnum == custnum).order_by(table.c.querytime.desc())
        return self.connection.execute(where)

    def getRecordsByCustnums(self, custnums):
        # For when it might match multiple
        table = self.tables['dnslog']
        where = table.select().where(table.c.custnum in custnums).order_by(table.c.querytime.desc())
        return self.connection.execute(where)
