from datetime import datetime
import re

def isDate(string):
    # Just, you know
    dateMatch = re.compile(r'^[0-9]{2}/[0-9]{2}/[0-9]{4}$')
    if re.match(dateMatch, string):
        return True
    else:
        return False
def isTime(string):
    # Makin' sure.
    timeMatch = re.compile(r'^[0-9]{2}(:[0-9]{2}){1,2}$')
    if re.match(timeMatch, string):
        return True
    else:
        return False

def compileDate(date, time):
    # For turning strings into datetime objects
    dateSplit = date.split('/')
    year = int(dateSplit[2])
    month = int(dateSplit[0])
    day = int(dateSplit[1])
    timeSplit = time.split(':')
    hour = int(timeSplit[0])
    minute = int(timeSplit[1])
    dt = datetime(year=year,month=month,day=day,hour=hour,
        minute=minute)
    print(dt)
    return dt

def convertDate(date, time):
    if isDate(date):
        if isTime(time):
            return compileDate(date, time)
        else:
            return compileDate(date, '00:00')
    else:
        return None

