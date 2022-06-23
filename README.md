[![Total alerts](https://img.shields.io/lgtm/alerts/g/camrossi/akb.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/camrossi/akb/alerts/)
[![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/camrossi/akb.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/camrossi/akb/context:javascript)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/camrossi/akb.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/camrossi/akb/context:python)
# Calico ACI Integration

This repo documents my steps to deploy a calico Cluster Integrated with ACI.
I use Terraform to deploy the ACI configuration and spin up the required Virtual Machines.

## ACI L3OUT design

The Calico cluster communicates with the ACI fabric via an External L3OUT.
In order to simplify the configuration and support Virtual Machine Mobility the design will adopt use the floating L3OUT feature.

### Floating L3 OUT Introduction

The  floating L3Out feature enables you to configure a L3Out without specifying logical interfaces. The feature saves you from having to configure multiple L3Out logical interfaces to maintain routing when virtual machines (VMs) move from one host to another. Floating L3Out is supported for VMware vSphere Distributed Switch (VDS) with ACI 4.2.(1) and physical domains starting from ACI 5.0(1)

In order to keep the design as flexible as possible and not to dictate the Virtualisation Technology adopted the physical domain approach will be the one used even if the virtualisation environemnt is based on VMware. This is particularly convenient as will allow the user to mix of different Virtualisations and Bare Metal servers at the same time.

For more details on Floating L3 Out refer to the [Cisco ACI Floating L3Out](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/kb/Cisco-ACI-Floating-L3Out.html) documentation.

Terminology refresher:

* Anchor Node: Are the routers where the routing peering is formed. There is no requirement on the number  of leaf switches acting as the anchor leaf node. As of ACI 5.1(3) an ACI leaf can have up to 400 BGP sessions.

* Non-anchor Node:  The non-anchor leaf node does not create any routing sessions for L3Out peering. It acts as a passthrough between the anchor node and the L3Out router. A non-anchor leaf node has the floating IP address and can have a floating secondary IP, if needed.. If it is a VMware vDS VMM domain, the floating IP address is deployed only when the virtual rotuer is connected to the leaf node. If it is a physical domain, and the leaf port uses AEP that has an L3Out domain associated to the floating L3Out, the floating IP address is deployed. The floating IP address is the common IP address for non-anchor leaf nodes. It is used to locate the router virtual machine (VM) if it moves behind any non-anchor leaf node through the data path.

* Floating IP: A common internal IP for non anchor leaf nodes to communicate with anchor leaf node.

### ACI design

The ACI configuration will follow the Floating L3OUT architecture described in the [Cisco Application Centric Infrastructure Calico Design White Paper](https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/application-centric-infrastructure/white-paper-c11-743182.html)

## The Kubernetes Cluster

The cluster is composed by 3 masters and N workers.
The control plane redundancy is ensured by deploying HaProxy and KeepaliveD.

A few add-ons are also installed on the cluster:

* Helm
* Nginx Ingress
* kubectl bash completion
* kubernetes dashboard
* Kustomize
* metric server: the default config is modified to add the `--kubelet-insecure-tls` since all the certificates are self signed
* Guestbook demo application exposed via ingress. Access via: http://ingress_ip/ this is not ideal, is just for demo purposes
* Gold Pinger

## UI

All the configurations can be done via the integrated webui.
Just execture the `appflask.py` file from the `terraform` directory

### Visibility

A visualization tool `vkaci` is also deployed on the cluster. It is exposed as a service and can be used to visualize the cluster topology.

## Open Issues

* L3OUT ECMP is used to load balance traffic to the services running in the cluster: Every node that has a POD for an exposed service will advertise a /32 host route for the service IP. Currently ACI does not support Resilient hashing for L3out ECMP. This means that if the number of ECMP paths are changed (scaling up/down a deploument could result in that as well as node failure) the flows can potentially be re-hashed to a different nodes resulting in connections resets. There is currently a feature request opened to support Resilient hashing for L3out ECMP: US9273

## Advacned 

### Raspberry Pi testing
We have been testing NKT and VKACI on 3 Raspberry Pis nodes with Ubuntu 20.4. If you plan to test the same here a few tips:

* Configure passwordless sudo
* CRI-O supports ARM64 Ubuntu starting from v1.24 
* edit the `/boot/firmware/cmdline.txt` and enable the following options
  * cgroup_enable=cpuset
  * cgroup_enable=memory
  * cgroup_memory=1
* Check the maximum MTU supported by the Rpi ethernet interfaces, not all support jumbo MTU. use ` ip -d link list` and look for `maxmtu`
