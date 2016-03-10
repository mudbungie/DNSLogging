# Host class for associating the IP address that we get out of the DNS logs
# with MAC addresses that we have in the RADIUS DB. Uses SNMP to check in with
# the client radio

# For the record, this would be like 20 minutes of work with easysnmp, but 
# for the life of me, I can't get OpenBSD to run it
# Ultimately, I'm just invoking a subshell to hadnle it with native snmpwalk

# gotta get our SNMP community string
from Config import config
import ipaddress
from snmp_helper import snmp_get_oid,snmp_extract
from subprocess import getoutput, call

class Host:
    # For getting information about clients from RADIUS, given an IP
    def __init__(self, ip):
        # Authenticate your inputs
        # Will throw an exception, if it isn't an IPv4 address
        ipaddress.IPv4Address(ip)
        self.ip = ip

    def getMac(self):
        # I know, I know, I hate myself too. Forking for this is atrocious.
        # If I had literally any other way to do it.
        snmpwalkBase = ['snmpwalk', '-c', config['snmp']['community'],
                            '-v', '1', self.ip]
        # Figure out how many interfaces the device has
        interfacesCommand = snmpwalkBase + ['IF-MIB::ifNumber.0']
        numberOfInterfaces = getoutput(interfacesCommand)
        print(numberOfInterfaces)

        # Use SNMP to pull the MAC address from the IP

        # list of mibs that refer to MAC addresses. The radios are inconsistent
        # with their usage of interfaces, so I can't trust them to be correct.
        # compiled through iter
        
        #MacMibs = #FIXME find out what the MIBs are for MAC addresses
        #IpMibs =#FIXME find out what the MIBs are for IP addresses
        #device = snmp_get_oid(self.ip, config['snmp']['community'], 161)
        #for IpMac in IpMibs:
        #    IpAddress = snmp_get_oid(device, oid=IpMib)
        #    if IpAddress == self.ip:
        #        self.mac = 
            
    def isItTheRightAddress(self):
        pass
        ## SNMP startup
        #session = Session(hostname = self.ip,
        #                    community = config['snmp']['community'],
        #                    version = 1)
        #MAC = session.get('IF-MIB::ifPhysAddress.2')
        #print(MAC)


if __name__ == '__main__':
    a = Host('172.24.42.23')
    a.getMac()
