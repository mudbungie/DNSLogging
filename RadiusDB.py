# For getting data from the RADIUS database.
# RADIUS has huge latency for unknown reasons, so calls to this DB are
# designed to be very batch-ey.

from Database import Database

class RadiusDB(Database):
    def __init__(self, databaseConfig):
        self.initDB(databaseConfig)
        tables = ['username_mac']
        self.initTables(tables)

    def getMacCustIdMapping(self):
        # Pull the username_mac table, which is poorly named, and build it
        # into a dict. The username field is actually custid from freeside.
        table = self.tables['username_mac']

        radQuery = table.select()
        radRecords = self.connection.execute(radQuery)

        radData = {}
        for radRecord in radRecords:
            # Make sure that it's actually a custid, this table is dirty
            if radRecord.username[0].isdigit():
                # Reformat the MAC address
                # Also, the column names are absurd, just roll with it
                usableMac = radRecord.Name_exp_2.replace('-', ':').lower()
                # Did I tell you, or what? Name_exp_2!?
                # Next, we scrub alpha characters from the username
                # Those are in there for reasons about which I don't care.
                custid = ''.join(c for c in radRecord.username if c.isdigit())
                radData[usableMac] = custid
        return radData

        


