# This is a command-line executable that will return all DNS records made by a
# customer when provided his/her name.  

#!/usr/local/bin/python3

import Database
from sys import argv

class Customer:
    def __init__(self, custid):
        # 
        
def findCustomersByName(database, name):
    # Names only exist in freeside, find them there
    custRecords = database.findFreesideCustomers(name)
    return custRecords

def returnDNSRecords(database, customer):
    

if __name__ == '__main__':
    freesidedb = Database(config['databases']['freeside'])
    dnslogdb = Database(config['databases']['dnslog'])

    if len(argv) < 2:
        # If they don't give me a name, there is nothing to do.
        print("Please provide a name as an argument. "
        print("For example: $ ./CheckDNSLogs.py J.R. Bob Dobbs")
        return False
    else:
        argv.pop[0]
        # Take the arguments, put wildcards in them, and hand it off to freeside to give us hits.
        matchString = '%'.join(argv)
        # Get matching customers from the database
        customers = findCustomersByName()

        if len(customers) == 0:
            # No matches, nothing to do
            print("No matches for that name in the records.")
            return False

        elif len(customers != 1):
            # If they get multiple results, make them choose
            counter = 0
            print("Multiple matches found! Did you mean: ")
            for customer in customers:
                print(str(counter) + ': ' + customer.payname + ' ' + customer.company)
                counter += 1
            choice = False
            # Until they chose something an item from the list
            while not type(choice) == int and not 0 <= choice <= counter:
                choice = input('Please choose [0-' + str(counter - 1) + ']')

        else:
            # There's only one item, so take that one
            choice = 0    
        returnDNSRecords(customers[choice])
