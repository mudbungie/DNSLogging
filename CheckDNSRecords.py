#!/usr/local/bin/python3
# This is a command-line executable that will return all DNS records made by a
# customer when provided his/her name.  

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

def searchRecordsByIP(ip):
    dnslogdb = DNSLogDB(config['databases']['dnslog'])
    records = dnslogdb.getRecordsByIP(ip)
    htmlFormatRecords(records)
    return records

def searchRecordsByName(name):
    dnslogdb = DNSLogDB(config['databases']['dnslog'])
    freesidedb = FreesideDB(config['databases']['freeside'])
    # Important to note that this can return more than one host.
    # IP searches are more specific.
    custs = freesidedb.getCustByName(name)
    custnums = []
    for cust in custs:
        custnums.append(cust.custnum)
    records = dnslogdb.getRecordsByCustnums(custnums)
    return records 

def searchLogs(string):
    if matchIP(string):
        # Then it's an IP address, so do a search for matching IPs.
        records = searchRecordsByIP(string)
    else:
        # Otherwise, check if it matches any names.
        records = searchRecordsByName(string)
    return records

def htmlFormatRecords(records):
    html = '<table>\n'
    html += '<tr><td>Date</td><td>Request</td></tr>\n'
    for record in records:
        html += '<tr>'
        html += '<td>' + str(record.querytime) + '</td>'
        html += '<td>' + record.request + '</td>'
        html += '\n'
    html += '</table>'
    return html

def getWebTable(string):
    # Takes a request from a web input, gives back a formatted block of HTML
    print('whatever')
    print(string)
    records = searchLogs(string)
    print(len(records))
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

