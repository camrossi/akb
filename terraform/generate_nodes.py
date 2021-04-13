import ipaddress

# Just a loop that add 1 to the IP and the AS number to automatically generate the list of nodes. 

subnet = ipaddress.ip_network("192.168.2.0/24")
as_number = 64501
nodes = 10
masters = 3
racks = 2

i = 1
m = 0
while i <= nodes:
    if masters > m:
        print("{")
        print('    hostname        = "master-{}"'.format(i))
        print('    ip              = "{}/{}"'.format(subnet[i], subnet.prefixlen))
        print('    local_as        = "{}"'.format(as_number))
        print('    rack_id        = "{}"'.format(i % racks + 1))
        print("},")
        m = m +1 
    else:
        print("{")
        print('    hostname        = "worker-{}"'.format(i - masters))
        print('    ip              = "{}/{}"'.format(subnet[i], subnet.prefixlen))
        print('    local_as        = "{}"'.format(as_number))
        print('    rack_id        = "{}"'.format(i % racks + 1))
        print("},")
    i += 1
    as_number += 1
