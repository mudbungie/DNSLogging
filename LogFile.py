# For managing logfiles generated directly to disk by rsyslog. 
# Mostly handles efficient copying, and maintenance of working files.
# Splits lines up, and passes them to the init function on FileLogEntry
# for parsing. The primary intent of this class is to avoid write 
# conflicts with rsyslog.

# One oddity in this system is that the LogFile object connects directly to the
# database, and uploads to it. This is explicitly just to prevent huge log 
# files from being loaded into RAM in initialization.

import os
import psutil
# FIXME delete; just here for some diagnostics
from datetime import datetime

import sqlalchemy.exc

from LogEntry import FileLogEntry, NotADNSRecord

class LogFile:
    def __init__(self, fileName, database, radiusdb):
        # The file it eats from, and the DB that it, umm, evacuates to
        self.logFileName = fileName
        self.database = database
        self.radiusdb = radiusdb
    def moveToWorkingFile(self):
        # Append .working to the filename
        self.workingFileName = self.logFileName + '.working'
        try:
            os.rename(self.logFileName, self.workingFileName)
        except FileNotFoundError:
            # Usually happens if the process is invoked without provileges
            # If it does, the .working should exist.
            pass
        # Rsyslogd writes to file by inode, and doesn't notice when you move 
        # it, so you have to send a sighup in order to trigger it to start 
        # writing a new file.
        for process in psutil.process_iter():
            try:
                if process.name() == 'rsyslogd':
                    process.send_signal(psutil.signal.SIGHUP)
            except psutil.NoSuchProcess:
                pass

    def parseWorkingFile(self):
        # Break the file into lines, make LogEntry objects out of it
        with open(self.workingFileName, 'r', 
            errors='surrogateescape') as workingFile:
            for line in workingFile:
                try:
                    # Read the log file
                    log = FileLogEntry(line)
                    # Check ARP to associate the IP with MAC
                    log.getMac(self.database)
                    # Check RADIUS to associate MAC with custid
                    log.getCustNum(self.radiusData)
                    # Insert record
                    log.commit(self.database)
                except NotADNSRecord:
                    # In case of any untoward data, log it.
                    with open(self.logFileName + '.error', 'a',
                        errors='surrogateescape') as errorFile:
                        errorFile.write(line)

    def purgeWorkingFile(self):
        os.remove(self.workingFileName)
        # In case you want to preserve the original logs for debugging
        #rightnow = datetime.now().strftime('%s')
        #os.rename(self.workingFileName, self.workingFileName + rightnow)
    def updateRadiusData(self):
        self.radiusData = self.radiusdb.getMacCustIdMapping()
    def digestFile(self):
        # Update the RADIUS data correlating macs to custids
        try:
          self.updateRadiusData()
        except sqlalchemy.exc.OperationalError:
          print('Radius data update failure')
        # Move the file to a working location
        self.moveToWorkingFile()
        # Read everything into LogEntries
        self.parseWorkingFile()
        # Delete the file
        self.purgeWorkingFile()
        return True
    def digestFucked(self):
        self.workingFileName = self.logFileName
        self.updateRadiusData()
        self.parseWorkingFile()
        self.purgeWorkingFile()
