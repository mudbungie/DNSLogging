# Database subclass for interacting with Freeside

from Database import Database
import sqlalchemy as sqla

class FreesideDB(Database):
    def __init__(self, databaseConfig):
        self.initDB(databaseConfig, reflect=False)
        tables = ['cust_main']
        self.initTables(tables)

    def getCustByName(self, name):
        table = self.tables['cust_main']

        # We might search by billing name or company name
        billingOrCompany = sqla.or_(table.c.payname == name, 
            table.c.company == name)
        # We might also search by first and last name, which is two fields
        try:
            names = name.split() # Break on spaces,
            firstName = names[0] # take first
            lastName = names[-1] # and last.
        except KeyError:
            # No spaces
            lastName = names[0]
        firstAndLast = sqla.and_(table.c.first == firstName, 
            table.c.last == lastName)

        nameOrBillingOrCompany = sqla.or_(billingOrCompany, firstAndLast)
        custsByName = table.select().where(nameOrBillingOrCompany)
        custs = self.connection.execute(custsByName)
        # Remember that this gives the recrods proxy object, not the numbers
        return custs

    def getCustByCustnum(self, custnum):
        table = self.tables['cust_main']
        custQuery = table.select().where(table.c.custnum == custnum)
        custs = self.connection.execute(custQuery)
        return custs.fetchone()

    def getAllCusts(self):
        table = self.tables['cust_main']
        custQuery = table.select()
        custs = self.connection.execute(custQuery)
        return custs
