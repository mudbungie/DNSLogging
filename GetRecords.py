#!/usr/local/bin/python3.4

# This is the executable for this project. When run, it triggers a parse of the
# current records, and continues that process until killed.

from LogFile import LogFile
from Database import Database
from Config import config
from time import sleep

if __name__ == '__main__':
    db = Database(config['databases']['syslog'])
    dnslogfile = LogFile(config['inputs']['logFile'], db)
    while True:
        dnslogfile.digestFile()
        sleep(1)
