import ipaddress

# Just a loop that add 1 to the IP and the AS number to automatically generate the list of nodes. 

subnet = ipaddress.ip_network("192.168.12.0/24")

v6subnet = ipaddress.ip_network("2001:db8:12::/56")
as_number = 650011
nodes = 50
racks = 2

i = 1
m = 0
while i <= nodes:
    print("{")
    print('    "hostname"        : "calico-{}",'.format(i))
    print('    "ip"              : "{}/{}",'.format(subnet[i], subnet.prefixlen))
    print('    "ipv6"            : "{}/{}",'.format(v6subnet[i], v6subnet.prefixlen))
    print('    "local_as"        : "{}",'.format(as_number))
    print('    "rack_id"         : "{}",'.format(i % racks + 1))
    print('    "natip"           : ""')
    print("},")
    i += 1
