# This is for prividing precompiled assets to the web interface. The first 
# thing that this is for is the json of every user's information for form 
# autocompletion. 

from Config import config
from DNSLogDB import DNSLogDB
from RadiusDB import RadiusDB
from FreesideDB import FreesideDB
from Customer import FSCustomer
import json

def getCustJson():
    # We're going to select every user in Freeside
    fsdb = FreesideDB(config['databases']['freeside'])
    custRecords = fsdb.getAllCusts()

    # Then compile all of their JSON into a big string
    # NOTE: This is done in a manner which seems backwards. It is so because 
    # it is used for autocompletion in the browser, so the key needs to be
    # the human-readable string.
    
    # This is for making a dictionary
    '''
    customers = {}
    for custRecord in custRecords:
        cust = FSCustomer(custRecord)
        for nametype, name in cust.names.items():
            customers[name] = cust.custnum
        #customers[cust.custnum] = cust.names
    '''
    # This is for making a list
    customers = []
    for custRecord in custRecords:
        cust = FSCustomer(custRecord)
        for nametype, name in cust.names.items():
            if not name == None and not name in customers:
                customers.append(name)
    jsonComp = json.dumps(customers)
    return jsonComp

### The following classes are for a legacy implementation. I intend to reuse them.

class UserProfile:
    # Class that gathers and compiles information regarding a single user 
    # into JSON.
    # Needs to output JSON with First+Last, Payname, Company, IP, and MAC
    def __init__(self, cust, macs, ips):
        # Start out with a record object, so we'll have to unpack it.
        self.first = cust.first
        self.last = cust.last
        self.name = self.first + ' ' + self.last
        self.company = cust.company
        self.payname = cust.payname
        self.custnum = cust.custnum
        # Usually, there is just one device on an account, but sometimes there
        # are more, so these are lists.
        self.macs = macs
        self.ips = ips
    def render(self):
        # Give back a string of JSON
        out = json.dumps({self.custnum:({'first':self.first, 
                                        'last':self.last, 
                                        'name':self.name, 
                                        'company':self.company,
                                        'macs':self.macs,
                                        'ips':self.ips,
                                        'payname':self.payname,
                                        })})
        return out

def getUserProfiles():
    dnslogdb = DNSLogDB(config['databases']['dnslog'])
    fsdb = FreesideDB(config['databases']['freeside'])
    raddb = RadiusDB(config['databases']['radius'])
    # Build dicts of relational network data.
    custMacs = raddb.getCustMacMapping()
    macIps = dnslogdb.getMacIps()
    #for mac, ip in macIps.items():
    #    print(mac)
    #    print(ip)
    #    pass
    #return False
    # Get, parse data for each customer
    custs = fsdb.getAllCusts()
    userProfiles = []
    for cust in custs:
        try:
            # There is all sorts of errant data in here
            macs = custMacs[str(cust.custnum)]
            print(str(cust.custnum) + ' found')
        except KeyError:
            # So customers might not appear in RADIUS
            print(str(cust.custnum) + ' not found')
            print('Error after: '+ str(len(userProfiles)) + ' profiles')
            macs = []
        ips = []
        for mac in macs:
            try:
                ips += macIps[mac]
            except:
                print('No match for ' + mac)
        userProfiles.append(UserProfile(cust, macs, ips))
    print('There are ' + str(len(userProfiles)) + ' userProfiles')
    # Concatenate it into a big JSON string
    json = ''
    for userProfile in userProfiles:
        json += (userProfile.render())
    #profileRenders = []
    #for userProfile in userProfiles:
    #    profileRenders.append(userProfile.render())
    #json.dumps(profileRenders)
    return json
'''
class jsonObject:
    def render(self):
        # Render the data for display on the web
        json = '{'
        json.append(renderBlock())

    def renderKeypair(key, value):
        json = '"' + key + '":' 
        if type(value) == str:
            json.append('"')
            json.append(value)
            json.append('"')
        elif type(value) == bool:
            if value == True:
                json.append('true')
            else:
                json.append('false')
        elif type(value) == int or type(value) == float:
            json.append(str(value))
        elif type(value) == list:
            json.append(renderList(key, value))
        return json

    def renderSequence(keypairs, title=None, seqtype=None):
        # If you pass a title, it does all the wrapping, so you'll need a
        # seqtype as well. Usable types are 'list'([]) and 'block'({})
        json = ''
        if title:
            json.append('"' + title + '":')
            if seqtype == 'list':
                enclosers = ['[', ']']
            elif seqtype == 'block':
                enclosers = ['{', '}']
        else:
            # I call this later, and it's easier to pass empty strings than
            # check settings
            enclosers = ['','']
        json.append(enclosers[0])
        # The JSON spec, being dumb, doesn't allow for trailing commas
        # so you have to do the first element differently.
        json = strings.pop()
        for keypairs in keypairs:
            json.append(',')
            json.append(renderKeypair(keypair))
        json.append(enclosers[1])
        return json

    def renderBlock(title, keypairs):
        # Take a bunch of values, and render them in an enclosed JSON block
        json.append(renderSequence(keypairs), title=title, seqtype='block')

    def renderList(title, keypairs):
        # Take a bunch of values, render them in an enclosed JSON list
        json.append(renderSequence(keypairs), title=title, seqtype='list')
'''
