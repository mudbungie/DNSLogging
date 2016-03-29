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

    def getMacIps(self):
        # Returns an inverted mapping of the previous function, for reversed
        # lookups. Used in web interface. Unfortunately, nothing is unique, 
        # so goodbye nice and efficient dicts, hello list of tuples.
        arpRecords = self.tables['arp']
        arpQuery = arpRecords.select().where(arpRecords.c.expired == None)
        arpRecords = self.connection.execute(arpQuery)

        # Make a dict indexed by MAC
        macIps = {}
        for arpRecord in arpRecords:
            try:
                # Append the IP to the existing MAC
                macIps[arpRecord.mac].append(arpRecord.ip)
            except KeyError:
                # Unless it's new, in which case, initialize it.
                macIps[arpRecord.mac] = [arpRecord.ip]
        return macIps

    def getMac(self, ip, time):
        # Just look in the local dict. Since I'm shorthanding the table, 
        # there's no expiry check.
        try:
            mac = self.mac[ip]
        except:
            mac = None
        return mac
    
    def getCustRecords(self, table, whereclause):
        # Get records according to some where clause
        query = table.select().where(whereclause).order_by(table.c.querytime.desc())
        records = self.connection.execute(query)
        return records
    
    #FIXME This code written under deadline, not DRY. Need to debloat
    def getRecordsByIP(self, ip, start=None, stop=None):
        table = self.tables['dnslog']
        # If there is a chronological restriction...
        if start and stop:
            print('chronological filter matched')
            query = table.select().where(sqla.and_(table.c.client_ip == ip, 
                table.c.querytime > start,
                table.c.querytime < stop)).order_by(table.c.querytime.desc())
        elif start:
            # Make sure that it's younger than the specified timestamp
            query = table.select().where(sqla.and_(table.c.client_ip == ip,
                table.c.querytime > start)).order_by(table.c.querytime.desc())
        elif stop:
            # Make sure that it's older than the specified timestamp
            query = table.select().where(sqla.and_(table.c.client_ip == ip,
                table.c.querytime < stop)).order_by(table.c.querytime.desc())
        else:
            # If there's no chronology, just return everything
            query = table.select().where(table.c.client_ip == ip).\
                order_by(table.c.querytime.desc())
        print(query)
        return self.connection.execute(query)

    def getRecordsByCustnum(self, custnum):
        table = self.tables['dnslog']
        where = table.select().where(table.c.custnum == custnum).order_by(table.c.querytime.desc())
        return self.connection.execute(where)

    def getRecordsByCustnums(self, custnums, start=None, stop=None):
        # For when it might match multiple
        table = self.tables['dnslog']
        # All name matches are returned, so we iterate
        for custnum in custnums:
            # If there is a chronological restriction...
            if start and stop:
                print('chronological filter matched')
                query = table.select().where(sqla.and_(table.c.custnum == custnum, 
                    table.c.querytime > start,
                    table.c.querytime < stop)).order_by(table.c.querytime.desc())
            elif start:
                # Make sure that it's younger than the specified timestamp
                query = table.select().where(sqla.and_(table.c.custnum == custnum,
                    table.c.querytime > start)).order_by(table.c.querytime.desc())
            elif stop:
                # Make sure that it's older than the specified timestamp
                query = table.select().where(sqla.and_(table.c.custnum == custnum,
                    table.c.querytime < stop)).order_by(table.c.querytime.desc())
            else:
                # If there's no chronology, just return everything
                query = table.select().where(table.c.custnum == custnum).\
                    order_by(table.c.querytime.desc())
            print(query)
            return self.connection.execute(query)
                # Make sure that it's younger than the specified timestamp
