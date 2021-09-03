apic = {
  username = "ansible"
  url = "https://fab2-apic1.cam.ciscolabs.com"
  cert_name = "ansible.crt"
  private_key = "/home/cisco/Coding/ansible.key"
}
vc = {
  url               = "vc2.cam.ciscolabs.com"
  username          = "administrator@vsphere.local"
  pass              = "123Cisco123!"
  dc                = "STLD"
  datastore         = "BM01"
  cluster           = "Cluster"
  dvs               = "ACI"
  port_group        = "CalicoL3OUT_300"
  vm_template       = "Ubuntu20-Template"
  vm_folder         = "Calico2.0"
}

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
    int_prof_name_v6       = "FloatingSVI_V6"
    #For now I just use a catch all EPG with 0.0.0.0/0
    def_ext_epg         = "catch_all"
    def_ext_epg_scope   = ["import-security", "shared-security", "shared-rtctrl", ]
    # The Physcal domain: All ports mapped to this PhysDom will get programmed with VLAN_ID
    physical_dom        = "Fab2"
    # secondary_ip is the default GW for the calico nodes
    secondary_ip        = "192.168.2.254/24"
    secondary_ipv6      = "2001:db8:42:00::254/56"
    # Used internally for leaf to leaf communicaiton. 
    floating_ip         = "192.168.2.253/24"
    floating_ipv6       = "2001:db8:42:00::253/56"
    # SVI VLAN ID
    vlan_id             = 300
    local_as            = 65002
    contract            = "default1"
    mtu                 = 9000
    bgp_pass            = "123Cisco123"
    #Limit the number of prefixes that any calico node can advertise to 500.
    #If you go above the additional prefixes will be Rejected. 
    max_node_prefixes   = 500
    dns_domain = "cam.ciscolabs.com"
    dns_servers = ["10.67.185.100"]
    # Anchor node list and configuration.
    anchor_nodes = [
        {
        node_id         = 201
        pod_id          = 1
        rtr_id          = "1.1.4.201"
        primary_ip      = "192.168.2.201/24"
        primary_ipv6    = "2001:db8:42:00::201/56"
        rack_id         = "1"
        },
        {
        node_id         = 202
        pod_id          = 1
        rtr_id          = "1.1.4.202"
        primary_ip      = "192.168.2.202/24"
        primary_ipv6    = "2001:db8:42:00::202/56"
        rack_id         = "1"
        },
        {
        node_id         = 203
        pod_id          = 1
        rtr_id          = "1.1.4.203"
        primary_ip      = "192.168.2.203/24"
        primary_ipv6    = "2001:db8:42:00::203/56"
        rack_id         = "2"
        },
        {
        node_id         = 204
        pod_id          = 1
        rtr_id          = "1.1.4.204"
        primary_ip      = "192.168.2.204/24"
        primary_ipv6    = "2001:db8:42:00::204/56"
        rack_id         = "2"
        }
    ]
}

# You MUST have 3 masters and N workers. 
# The 1st node is the primary master. 2nd and 3rd are the master replices and everything else is a worker.
# If you do not have 3 master the script will break...Need to make it more generic eventually
calico_nodes = [{
    hostname        = "master-1"
    ip              = "192.168.2.1/24"
    ipv6            = "2001:db8:42::1/56"
    local_as        = "64501"
    rack_id         = "2"
},
{
    hostname        = "master-2"
    ip              = "192.168.2.2/24"
    ipv6            = "2001:db8:42::2/56"
    local_as        = "64502"
    rack_id         = "1"
},
{
    hostname        = "master-3"
    ip              = "192.168.2.3/24"
    ipv6            = "2001:db8:42::3/56"
    local_as        = "64503"
    rack_id         = "2"
},
{
    hostname        = "worker-1"
    ip              = "192.168.2.4/24"
    ipv6            = "2001:db8:42::4/56"
    local_as        = "64504"
    rack_id         = "1"
},
{
    hostname        = "worker-2"
    ip              = "192.168.2.5/24"
    ipv6            = "2001:db8:42::5/56"
    local_as        = "64505"
    rack_id         = "2"
},
{
    hostname        = "worker-3"
    ip              = "192.168.2.6/24"
    ipv6            = "2001:db8:42::6/56"
    local_as        = "64506"
    rack_id         = "1"
},
{
    hostname        = "worker-4"
    ip              = "192.168.2.7/24"
    ipv6            = "2001:db8:42::7/56"
    local_as        = "64507"
    rack_id         = "2"
},
{
    hostname        = "worker-5"
    ip              = "192.168.2.8/24"
    ipv6            = "2001:db8:42::8/56"
    local_as        = "64508"
    rack_id         = "1"
},
{
    hostname        = "worker-6"
    ip              = "192.168.2.9/24"
    ipv6            = "2001:db8:42::9/56"
    local_as        = "64509"
    rack_id         = "2"
},
{
    hostname        = "worker-7"
    ip              = "192.168.2.10/24"
    ipv6            = "2001:db8:42::a/56"
    local_as        = "64510"
    rack_id         = "1"
}
]

k8s_cluster = {
    kube_version        = "1.22.1-00"
    crio_version        = "1.22"
    OS_Version          = "xUbuntu_20.04"
    control_plane_vip   = "192.168.2.100"
    vip_port            = 8443
    haproxy_image       = "haproxy:2.3.6"
    keepalived_image    = "osixia/keepalived:2.0.20"
    keepalived_router_id= "51"
    kubeadm_token       = "fqv728.htdmfzf6rt9blhej"
    node_sub            = "192.168.2.0/24"
    node_sub_v6         = "2001:db8:42:0::/56"
    pod_subnet          = "10.1.0.0/16"
    pod_subnet_v6       = "2001:db8:43:0::/56"
    cluster_svc_subnet  = "192.168.8.0/22"
    cluster_svc_subnet_v6  = "2001:db8:44:1::/112"
    ntp_server          = "72.163.32.44"
    time_zone           = "Australia/Sydney"
    docker_mirror       = "10.67.185.120:5000"
    ingress_ip          = "192.168.3.1"
    external_svc_subnet = "192.168.3.0/24"
    external_svc_subnet_v6 = "2001:db8:44:2::/112"

  }