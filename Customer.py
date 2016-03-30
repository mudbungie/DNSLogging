# A generic class for customers
import json

class Customer:
    # Generic class, to be subscripted in a manner that provides for its 
    # initialization. Provides mobility in how you make the record/
    
    def writeJSON(self):
        out = json.dumps({self.custnum:self.names})
        return out

class FSCustomer(Customer):
    def __init__(self, fsRecord):
        # Unpack a database record
        self.custnum = fsRecord.custnum
        self.first = fsRecord.first
        self.last = fsRecord.last
        self.fullname = self.first + self.last
        self.payname = fsRecord.payname
        self.company = fsRecord.company
        self.names = {'name':self.fullname,
            'payname':self.payname,
            'company':self.company}
