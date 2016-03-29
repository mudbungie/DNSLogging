# A generic class for customers
import json

class Customer:
    # Generic class, to be subscripted in a manner that provides for its 
    # initialization. Provides mobility in how you make the record/
    def writeJSON(self):
        out = json.dumps({self.custnum:({'name':self.name,
                                        'payname':self.name,
                                        'company':self.company.
                                        })})
        return out

class FSCustomer(Customer):
    def __init__(self, fsRecord):
        # Unpack a database record
        self.custnum = fsRecord.custnum
        self.first = fsRrecord.first
        self.last = fsRecord.last
        self.name = self.first + self.last
        self.payname = fsRecord.payname
        self.company = fsRecord.company

