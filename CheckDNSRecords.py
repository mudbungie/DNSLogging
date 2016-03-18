#!/usr/local/bin/python3
# This is a command-line executable that will return all DNS records made by a
# customer when provided his/her name.  

from Config import config
from Database import Database
from sys import argv

def printUsage():
    print('Usage:')
    print('CheckDNSRecords.py -a [ADDRESS]')
    print('CheckDNSRecords.py -n [NAME]')

def printRecords(records):
    for record in records:
        print(record.querytime, record.request)
    
if __name__ == '__main__':
    try:
        if argv[1] == '-a':
            db = Database(config['databases']['dnslog'])
            records = db.getRecordsByIP(argv[2])
            printRecords(records)
        elif argv[1] == '-n':
            freesidedb = Database(config['databases']['freeside'])
            dnslogdb = Database(config['databases']['dnslog'])
            name = ' '.join(argv[2:])
            custs = freesidedb.getCustByName(name)
            if custs.rowcount == 0:
                print('No records matching that name')
                exit()
            elif custs.rowcount == 1:
                cust = custs.fetchone()
            else:
                # We've got too many matching records. Gotta delineate
                print('Multiple matches. Did you mean:')
                count = 0
                customers = []
                for cust in custs:
                    print('[' + str(count) + '] ' + cust.first + ' ' + 
                        cust.last + ' ' + str(cust.custnum))
                    count += 1
                    customers.append(cust)
                choice = int(input('selection: '))
                cust = customers[choice]
            records = dnslogdb.getRecordsByCustnum(cust.custnum)
            printRecords(records)
        else:
            printUsage()
    except IndexError:
        printUsage()

