# Host class for associating the IP address that we get out of the DNS logs
# with MAC addresses that we have in the RADIUS DB. Uses SNMP to check in with
# the client radio

from Config import config
import ipaddress
from easysnmp import Session

class Host:
    def __init__(self, ip):
        if type(ip) == str:
            self.ip = ipaddress.IPv4Address(ip)
        elif type(ip) == ipaddress.IPv4Address:
            self.ip = ip
        self.ip = ip
        self.getMac()

    def getMac(self):
        # Use SNMP to pull the MAC address from the IP

        # SNMP startup
        session = Session(hostname = self.ip,
                            community = config['snmp']['community'],
                            version = 1)
        MAC = session.get('IF-MIB::ifPhysAddress.2')
        print(MAC)

if __name__ == '__main__':
    a = Host('172.24.42.23')
