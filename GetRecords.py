#!/usr/local/bin/python3.4

# This is the executable for this project. When run, it triggers a parse of the
# current records, and continues that process until killed.

from LogFile import LogFile
from Database import Database
from Config import config
from time import sleep

if __name__ == '__main__':
    dnslogdb = Database(config['databases']['syslog'])
    radiusdb = Database(config['databases']['radius'])
    dnslogfile = LogFile(config['inputs']['logFile'], dnslogdb, radiusdb)
    while True:
        dnslogfile.digestFile()
        sleep(1)
