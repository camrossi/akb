#!/usr/local/bin/python3
import sys
import os
from kubernetes import client, config
from pyaci import Node
from pyaci import options
from pyaci import filters
import random
import logging

#If you need to look at the API calls this is what you do
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('pyaci').setLevel(logging.DEBUG)
if len(sys.argv) != 2:
    print("This commands takes only one argument, the pod name")
    exit()

apic_ip=os.environ.get("APIC_IPS").split(',')
# Get the APIC Model

pod_name= sys.argv[1]
pod = {}

# Configs can be set in Configuration class directly or using helper utility
#config.load_kube_config(config_file="./config")
config.load_incluster_config()

v1 = client.CoreV1Api()
ret = v1.list_pod_for_all_namespaces(watch=False)
#Load all the POD in Memory. 
for i in ret.items:
    pod[i.metadata.name] = {"ip": i.status.pod_ip, "ns": i.metadata.namespace, "node_ip": i.status.host_ip, "node_name": i.spec.node_name }

apic = Node('https://' + random.choice(apic_ip))
apic.useX509CertAuth(os.environ.get("CERT_USER"),os.environ.get("CERT_NAME"),'/usr/local/etc/aci-cert/user.key')

#Get all the bgpDomin in the right VRF. This is one per node.
#bgpPeers = apic.methods.ResolveClass('bgpPeer').GET(**options.filter(filters.Wcard('bgpPeer.dn', '.*/dom-common:calico/.*')))

try: 
    print("Looking for pod {} with IP {} on node {}/{}".format(pod_name, pod[pod_name]['ip'], pod[pod_name]['node_ip'], pod[pod_name]['node_name'] ))
except:
    print("Pod does noex exist")
    exit()

#Find the K8s Node IP/Mac
ep = apic.methods.ResolveClass('fvCEp').GET(**options.rspSubtreeChildren & 
                                            options.subtreeFilter(filters.Eq('fvIp.addr', pod[pod_name]['node_ip'])))[0]

#Find the mac to interface mapping 
path = apic.methods.ResolveClass('fvCEp').GET(**options.filter(filters.Eq('fvCEp.mac', ep.mac)) & options.rspSubtreeClass('fvRsCEpToPathEp'))[0]

#Get Path, there should be only one...need to add checks
for fvRsCEpToPathEp in path.fvRsCEpToPathEp:
    pathtDn = fvRsCEpToPathEp.tDn

print("The K8s Node is physically connected to: {}".format(pathtDn))
#Get all LLDP Neighbors 
lldp_neighbours = apic.methods.ResolveClass('lldpIf').GET(**options.filter(filters.Eq('lldpIf.portDesc',pathtDn)) & options.rspSubtreeClass('lldpAdjEp'))

print("LLDP Infos:")
for lldp_neighbour in lldp_neighbours:
    print("\t {} {}".format(lldp_neighbour.sysDesc, lldp_neighbour.id))
    for i in lldp_neighbour.lldpAdjEp:
        print("\t\t {}".format(i.sysName))

print("BGP Peer:")
bgpPeerEntry = apic.methods.ResolveClass('bgpPeerEntry').GET(**options.filter(filters.Wcard('bgpPeerEntry.dn', '.*/dom-common:calico/.*') & filters.Eq('bgpPeerEntry.addr',pod[pod_name]['node_ip'])))

for i in bgpPeerEntry:
    print("\t {}".format(i.dn.split("/")[2]))
