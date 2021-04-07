# Terraform Variables

The terraform variables are arranged in "objects" for ease of grouping and configuration simplicty. 
Below you can see an example configuration file with some detailed explanation where required. 
Each configuration object is explained as stand alone. 

## APIC Parameters

In this section you simply specify the username, certificate, private key and URL of your APIC.

Example:

```terraform
apic = {
  username = "username"
  cert_name = "username.crt"
  private_key = "path_to_private_key"
  url = "https://APIC_URL"
}
```

## Virtual Center

Use this section to specoify your VMware environment parameters:

* The credentilas to access your Virtual Center server
* You then also need to specify the following parameters:
  * dc: The name of your datacenter
  * datastore: The shared datastore where to deploy the VMs
  * cluster: the ESXi cluster where to deploy the VMs
  * dvs: Name of the Distributed Virtual Switch to use
  * port_group: Name of the Port Group to use, this must be created manually prior to running the terrafrm plan. 
  * vm_template: The anme of the VM template to clone from. I use linked clones so your templage must also have a snapshot. The latest snapshot is automatically used. 
  * vm_folder: A pre-existing folder where all the VMs are placed.

Since we are using a phisical domain with floating L3OUT any other hypervisor (or bare metal hosts) can be used, for now I only support VMWare, feel free to open an Issue or do a Pull Request if you add support for something else!

Example:

```terraform
vc = {
  url               = "VC_URL"
  username          = "username"
  pass              = "pass"
  dc                = "DataCetner_name"
  datastore         = "DataStore_name"
  cluster           = "Cluster_Name"
  dvs               = "DVS_Name"
  port_group        = "Port_Group_Name"
  vm_template       = "VM_Template_Name"
  vm_folder         = "VM_Folder_Name"
}
```

## ACI L3OUT Configuration Parameters

Currently a dedicated L3OUT is created for the cluster.
The VRF and Tenant can be dedicated or shared with other Clusters/Workloads however the VRF and Tenant must be created manually.
This is done for safety as Terraform will delete all the objects that it creates.
Connectivity from the cluster outside of ACI is done via Transit Routing on a shared L3OUT. The Shared L3OUT can be in the same tenant/vrf as the cluster or in the common tenant.

Use this section to specify your L3OUT parameters.

* name: The L3OUT name, this should be unique for each cluster.
* l3out_tenant: The name of the tenant where the L3OUT resides
* vrf_tenant: The name of the tenant where the VRF resides. This is done to allow you to place the l3out in Tenant X and the VRF in Common tenant.
* vrf_name: Name of the VRF for the cluster
* node_profile_name: Name of the Node Profile under the L3OUT
* int_prof_name: Name of the interface profile under the node_profile
* def_ext_epg: Currently a single extEPG is created for the cluster. This EPG has Longest-Prefix-Matches for all the subent used in the cluster (Node,Pod,Cluster Service and External Service)
* def_ext_epg_scope: Set the scope of the subnets under the def_ext_epg. This is a list of strings see the [l3_ext_subnet](https://registry.terraform.io/providers/CiscoDevNet/aci/latest/docs/resources/l3_ext_subnet#scope) documentation and the [ACI L3OUT](https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/application-centric-infrastructure/guide-c07-743150.html#L3Outsubnetscopeoptions) documentation for details
* bgp_pass: The BGP Password to secure the peering
* contract: This contract should already exists and it is consumed and provided by the def_ext_epg. It should then be Consumed/Provided by the shared L3OUT to provide connectivity to the Nodes. This contract should be pre-existing and is not created nor deleted by terraform.
* max_node_prefixes: Set the maximum number of routes ACI will accept from each of the Calico Nodes. If usure set it to 20000, the default value for ACI.
* dns_domain: The domain name
* dns_servers: List of DNS Servers to be configued in the Calico Nodes
* Floating SVI Specific parameters
  * physical_dom: This is required for the Floating SVI configuration. All the ports that are part of this physical domain will get programmed with the Floating SVI Vlan ID. Ideally you should create a dedicated Phisical Domain if possible to avoid programing the vlan toward hosts that are not part of the cluster.
  * secondary_ip: This is the anycast Gateway IP that is programmed on all the leaves part of the physical_dom. The Calico Nodes are configured to use this IP as default GW.
    * This IP MUST be in the same subnet as the Nodes.
  * floating_ip: Used internally for leaf to leaf communicaiton. Just pick a free IP. WARNING: DO NOT USE IT FOR ANYTHING ELSE
    * This IP MUST be in the same subnet as the Nodes.
  * vlan_id: The VLAN ID
  * local_as: ACI Local AS. Get it from APIC --> System --> System Setting --> BGP Route Reflector --> Austonomous System Number
  * mtu: The MTU of the floating SVI
* anchor_nodes: This is must contains the 2 ACI leaves that will act as anchor nodes. Refer to [Floating L3 OUT Introduction](../README.md) for a refresher. Currently onle 2 are supported. 
  * node_id: The numeric node ID
  * pod_id: The number of the POD where the node is configured in
  * rtr_id: The router ID, must be uniq in the VRF
  * primary_ip: The IP address of the node
    * This IP MUST be in the same subnet as the Nodes.

Example:

```terraform
l3out = {
    # Name of the L3OUT
    name                = "calico_l3out" 
    # L3OUT could be in any tenant
    l3out_tenant        = "common"
    # VRF can be in common or in the same tenant as the l3out_tenant
    vrf_tenant          = "common"
    vrf_name            = "calico"
    node_profile_name   = "NodePfl"
    int_prof_name       = "FloatingSVI"
    #For now I just use a catch all EPG with 0.0.0.0/0
    def_ext_epg         = "catch_all"
    def_ext_epg_scope   = ["import-security", "shared-security", "shared-rtctrl" ]
    bgp_pass            = "123Cisco123"
    max_node_prefixes   = 500
    contract            = "default1"
    dns_domain = "cam.ciscolabs.com"
    dns_servers = ["10.67.185.100"]
    # The Physcal domain: All ports mapped to this PhysDom will get programmed with VLAN_ID
    physical_dom        = "Fab2"
    # secondary_ip is the default GW for the calico nodes
    secondary_ip        = "192.168.2.254/24"
    # Used internally for leaf to leaf communicaiton. 
    floating_ip         = "192.168.2.253/24"
    # SVI VLAN ID
    vlan_id             = 300
    local_as            = 65002
    mtu                 = 9000
    #Limit the number of prefixes that any calico node can advertise to 500.
    #If you go above the additional prefixes will be Rejected. 
    # Anchor node list and configuration.
    anchor_nodes = [
        {
        node_id         = 201
        pod_id          = 1
        rtr_id          = "1.1.4.201"
        primary_ip      = "192.168.2.201/24"
        },
        {
        node_id         = 202
        pod_id          = 1
        rtr_id          = "1.1.4.202"
        primary_ip      = "192.168.2.202/24"
        }
    ]
}
```

## Kubernetes Cluster Configuration Parameters

Use this section to specify your Kubernetes Cluster Configuration parameters.

* kube_version: The version to use for the kubelet, kubectl and kubeadm package. On Ubuntu you can use `apt-cache show kubeadm | grep Version` to get the list of all the avaialble versions.  
* Crio Specific Parameters: Refer to the [CRIO Install Guide](https://github.com/cri-o/cri-o/blob/master/install.md) for installatio details
  * crio_version: The versioni to use for the crio package
  * OS_Version: The version of the operative system

* Control Plan redundancy: The cluster contains 3 master nodes. KueepaliveD and HapRoxy are used to load balance the load between the 3 masters.
  * control_plane_vip: The Virtual IP for the master nodes.
  * vip_port: The port for the VIP to listen to. Reccomend to use 8443 as is a standard value
  * haproxy_image: Haproxy image on docker hub
  * keepalived_image: keepalived image on docker hub
  * keepalived_router_id: The router ID number used by keepaliveD must be unique between clusters in the same subnet/vlan. You should not install 2 cluster in the same subnet/blan in the first place.
* kubeadm_token: To simplify the installation workflow is easier to pass a pre-generated kubeadm token. This is only used during install. 
* node_sub: The subnet for the nodes. This subnet is the same as the one used for the IP addresses that are allocated to the Floaring SVI and the Ancor Nodes
* pod_subnet: The subnet for the PODs. Keep in mind every Calico Nodes gets a /26 by default. Do your math before! if you want to have for example 64 nodes you need a /20 subnetas minimum or you won't have enough /26 to allocate!!
* cluster_svc_subnet: The Cluster-IP Service subnet
* external_svc_subnet: The External Service subnet used for Services of type LoadBalancer
* ntp_server: IP address or name of the DNS server, NTP is good... use NTP
* time_zone: The time zone in the standard unix format. Use `timedatectl list-timezones` to get a list of valid Time Zones
* docker_mirror: (Optional, set to "" to disable) in the format of IP:PORT configure CRIO to pull images from a dockerhub mirror. Very useful now that docker limits the pull youcan do. This DOES not install a mirror for you. You need to install one on your own. If you get stuck [This](docker_mirror.dm) is how I did it.
* ingress_ip: The cluster comes with a few add-ons, one is an Nginx Ingress controller. This parameter set its IP address. This must be a free address from the external_svc_subnet

```terraform
k8s_cluster = {
    kube_version        = "1.20.4-00"
    crio_version        = "1.20"
    OS_Version          = "xUbuntu_20.04"
    control_plane_vip   = "192.168.2.100"
    vip_port            = 8443
    haproxy_image       = "haproxy:2.3.6"
    keepalived_image    = "osixia/keepalived:2.0.20"
    keepalived_router_id= "51"
    kubeadm_token       = "fqv728.htdmfzf6rt9blhej"
    node_sub            = "192.168.2.0/24"
    pod_subnet          = "10.1.0.0/16"
    cluster_svc_subnet  = "192.168.8.0/22"
    ntp_server          = "72.163.32.44"
    time_zone           = "Australia/Sydney"
    docker_mirror       = "10.67.185.120:5000"
    ingress_ip          = "192.168.3.1"
    external_svc_subnet = "192.168.3.0/24"
  }
  ```

## Calico Nodes List

You MUST have 3 masters and N workers. The 1st node is the primary master, the 2nd and 3rd are the master replices and everything else are a workers.
If you do not have 3 master the script will break...

* calico_nodes: This is a list of nodes
  * hostname: The host name of the node
  * ip: The IP address of the node (IP/Sub format). The IP address MUST be insude the node_sub and MUST not overlap with any of the IPs used for the floating SVI.
  * local_as: eBGP AS Number. Every node must have a uniq AS Number.

Creating the node list manually can be a bit tedious, use the [generate_nodes.py](../terraform/generate_nodes.py) script to create the node list automatically.

Example:

```terraform
calico_nodes = [
   {
      "hostname"        = "master-1"
      "ip"              = "192.168.2.1/24"
      "local_as"        = "64501"
   },
   {
      "hostname"        = "master-2"
      "ip"              = "192.168.2.2/24"
      "local_as"        = "64502"
   },
   {
      "hostname"        = "master-3"
      "ip"              = "192.168.2.3/24"
      "local_as"        = "64503"
   },
   {
      "hostname"        = "worker-1"
      "ip"              = "192.168.2.4/24"
      "local_as"        = "64504"
   },
   {
      "hostname"        = "worker-2"
      "ip"              = "192.168.2.5/24"
      "local_as"        = "64505"
   },
   {
      "hostname"        = "worker-3"
      "ip"              = "192.168.2.6/24"
      "local_as"        = "64506"
   }
]
```