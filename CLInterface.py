#!/usr/local/bin/python3

# Chris wanted a CLI, so here it is.

from DNSLogDB import DNSLogDB
from Config import config
from sys import argv


if __name__ == "__main__":
    query = argv[1]
    print(query)
    db = DNSLogDB(config['databases']['dnslog'])
    records = db.getRecordsByTarget(query)
    for record in records:
        print(record.answeringserver, record.querytime, record.client_ip)
