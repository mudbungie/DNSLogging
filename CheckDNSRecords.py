#!/usr/local/bin/python3
# This is a command-line executable that will return all DNS records made by a
# customer when provided his/her name.  
# It's also used by the web system for the same purposes
#FIXME This got bloated, and I'm passing variables around like an idiot. Make 
# a class to handle all the web stuff.

from Config import config
from DNSLogDB import DNSLogDB
from FreesideDB import FreesideDB
from sys import argv
import ipaddress

def printUsage():
    print('Usage:')
    print('CheckDNSRecords.py -a [ADDRESS]')
    print('CheckDNSRecords.py -n [NAME]')

def printRecords(records):
    for record in records:
        print(record.querytime, record.request)

def matchIP(string):
    # Determine if a passed string is an IPv4 address.
    try:
        ipaddress.IPv4Address(string)
        return True
    except ipaddress.AddressValueError:
        return False

def searchRecordsByIP(ip, start, stop):
    dnslogdb = DNSLogDB(config['databases']['dnslog'])
    print(start)
    print(stop)
    records = dnslogdb.getRecordsByIP(ip, start, stop)
    #htmlFormatRecords(records)
    return records

def searchRecordsByName(name, start, stop):
    dnslogdb = DNSLogDB(config['databases']['dnslog'])
    freesidedb = FreesideDB(config['databases']['freeside'])
    # Important to note that this can return more than one host.
    # IP searches are more specific.
    custs = freesidedb.getCustByName(name)
    custnums = []
    for cust in custs:
        custnums.append(cust.custnum)
    records = dnslogdb.getRecordsByCustnums(custnums, start, stop)
    return records 

def searchLogs(string, start, stop):
    if matchIP(string):
        # Then it's an IP address, so do a search for matching IPs.
        records = searchRecordsByIP(string, start, stop)
    else:
        # Otherwise, check if it matches any names.
        records = searchRecordsByName(string, start, stop)
    return records

def htmlFormatRecord(record):
    html = '<tr>'
    html += '<td>' + str(record.answeringserver) + '</td>'
    html += '<td>' + str(record.querytime) + '</td>'
    html += '<td>' + str(record.request) + '</td>'
    #print(html)
    return html

def htmlFormatRecords(records):
    print('Formatter invoked')
    html = '<head><style>table td{border: 1px solid black;}</style></head>'
    html += '<table>'
    html += '<tr><td>DNSServer</td><td>Date</td><td>Request</td></tr>'
    count = 0
    for record in records:
        html += htmlFormatRecord(record)
        count += 1
    print('Iterated ' + str(count) + ' times')
    html += '</table>'
    return html

def getWebTable(string, start, stop):
    # Takes a request from a web input, gives back a formatted block of HTML
    print('Searching for: ' + string)
    records = searchLogs(string, start, stop)
    print('Returned ' + str(records.rowcount) + ' records')
    return htmlFormatRecords(records)

if __name__ == '__main__':
    try:
        if argv[1] == '-a':
            db = DNSLogDB(config['databases']['dnslog'])
            records = db.getRecordsByIP(argv[2])
            printRecords(records)
        elif argv[1] == '-n':
            freesidedb = FreesideDB(config['databases']['freeside'])
            dnslogdb = DNSLogDB(config['databases']['dnslog'])
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

