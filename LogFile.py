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

from LogEntry import FileLogEntry, NotADNSRecord

class LogFile:
    def __init__(self, fileName, database):
        # The file it eats from, and the DB that it, umm, evacuates to
        self.logFileName = fileName
        self.database = database
    def moveToWorkingFile(self):
        # Append .working to the filename
        self.workingFileName = self.logFileName + '.working'
        os.rename(self.logFileName, self.workingFileName)
        # Rsyslogd writes to file by inode, and doesn't notice when you move 
        # it, so you have to send a sighup in order to trigger it to start 
        # writing a new file.
        for process in psutil.process_iter():
            if process.name() == 'rsyslogd':
                process.send_signal(psutil.signal.SIGHUP)
    def parseWorkingFile(self):
        # Break the file into lines, make LogEntry objects out of it
        with open(self.workingFileName, 'r') as workingFile:
            for line in workingFile:
                try:
                    log = FileLogEntry(line)
                    log.commit(self.database)
                except NotADNSRecord:
                    # In case of any untoward data
                    pass
    def purgeWorkingFile(self):
            os.remove(self.workingFileName)
    def digestFile(self):
        # Move the file to a working location
        self.moveToWorkingFile()
        # Read everything into LogEntries
        self.parseWorkingFile()
        # Delete the file
        self.purgeWorkingFile()
        return True
