apic_username = "ansible"
apic_url = "https://fab2-apic1.cam.ciscolabs.com"
cert_name = "ansible.crt"
private_key = "/home/cisco/Coding/ansible.key"
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
dns_domain = "cam.ciscolabs.com"
dns_servers = ["10.67.185.100"]
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
    def_ext_epg_scope   = ["import-security", "shared-security", "shared-rtctrl", ]
    # The Physcal domain: All ports mapped to this PhysDom will get programmed with VLAN_ID
    physical_dom        = "Fab2"
    # secondary_ip is the default GW for the calico nodes
    secondary_ip        = "192.168.2.254/24"
    # Used internally for leaf to leaf communicaiton. 
    floating_ip         = "192.168.2.253/24"
    # SVI VLAN ID
    vlan_id             = 300
    local_as            = 65002
    contract            = "default1"
    mtu                 = 9000
    bgp_pass            = "123Cisco123"
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

# You MUST have 3 masters and N workers. 
# The 1st node is the primary master. 2nd and 3rd are the master replices and everything else is a worker.
# If you do not have 3 master the script will break...Need to make it more generic eventually
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
},
{
   "hostname"        = "worker-4"
   "ip"              = "192.168.2.7/24"
   "local_as"        = "64507"
},
{
   "hostname"        = "worker-5"
   "ip"              = "192.168.2.8/24"
   "local_as"        = "64508"
},
{
   "hostname"        = "worker-6"
   "ip"              = "192.168.2.9/24"
   "local_as"        = "64509"
},
{
   "hostname"        = "worker-7"
   "ip"              = "192.168.2.10/24"
   "local_as"        = "64510"
},
{
   "hostname"        = "worker-8"
   "ip"              = "192.168.2.11/24"
   "local_as"        = "64511"
},
{
   "hostname"        = "worker-9"
   "ip"              = "192.168.2.12/24"
   "local_as"        = "64512"
},
{
   "hostname"        = "worker-10"
   "ip"              = "192.168.2.13/24"
   "local_as"        = "64513"
},
{
   "hostname"        = "worker-11"
   "ip"              = "192.168.2.14/24"
   "local_as"        = "64514"
},
{
   "hostname"        = "worker-12"
   "ip"              = "192.168.2.15/24"
   "local_as"        = "64515"
},
{
   "hostname"        = "worker-13"
   "ip"              = "192.168.2.16/24"
   "local_as"        = "64516"
},
{
   "hostname"        = "worker-14"
   "ip"              = "192.168.2.17/24"
   "local_as"        = "64517"
},
{
   "hostname"        = "worker-15"
   "ip"              = "192.168.2.18/24"
   "local_as"        = "64518"
},
{
   "hostname"        = "worker-16"
   "ip"              = "192.168.2.19/24"
   "local_as"        = "64519"
},
{
   "hostname"        = "worker-17"
   "ip"              = "192.168.2.20/24"
   "local_as"        = "64520"
},
{
   "hostname"        = "worker-18"
   "ip"              = "192.168.2.21/24"
   "local_as"        = "64521"
},
{
   "hostname"        = "worker-19"
   "ip"              = "192.168.2.22/24"
   "local_as"        = "64522"
},
{
   "hostname"        = "worker-20"
   "ip"              = "192.168.2.23/24"
   "local_as"        = "64523"
},
{
   "hostname"        = "worker-21"
   "ip"              = "192.168.2.24/24"
   "local_as"        = "64524"
},
{
   "hostname"        = "worker-22"
   "ip"              = "192.168.2.25/24"
   "local_as"        = "64525"
},
{
   "hostname"        = "worker-23"
   "ip"              = "192.168.2.26/24"
   "local_as"        = "64526"
},
{
   "hostname"        = "worker-24"
   "ip"              = "192.168.2.27/24"
   "local_as"        = "64527"
},
{
   "hostname"        = "worker-25"
   "ip"              = "192.168.2.28/24"
   "local_as"        = "64528"
},
{
   "hostname"        = "worker-26"
   "ip"              = "192.168.2.29/24"
   "local_as"        = "64529"
},
{
   "hostname"        = "worker-27"
   "ip"              = "192.168.2.30/24"
   "local_as"        = "64530"
},
{
   "hostname"        = "worker-28"
   "ip"              = "192.168.2.31/24"
   "local_as"        = "64531"
},
{
   "hostname"        = "worker-29"
   "ip"              = "192.168.2.32/24"
   "local_as"        = "64532"
},
{
   "hostname"        = "worker-30"
   "ip"              = "192.168.2.33/24"
   "local_as"        = "64533"
},
{
   "hostname"        = "worker-31"
   "ip"              = "192.168.2.34/24"
   "local_as"        = "64534"
},
{
   "hostname"        = "worker-32"
   "ip"              = "192.168.2.35/24"
   "local_as"        = "64535"
},
{
   "hostname"        = "worker-33"
   "ip"              = "192.168.2.36/24"
   "local_as"        = "64536"
},
{
   "hostname"        = "worker-34"
   "ip"              = "192.168.2.37/24"
   "local_as"        = "64537"
},
{
   "hostname"        = "worker-35"
   "ip"              = "192.168.2.38/24"
   "local_as"        = "64538"
},
{
   "hostname"        = "worker-36"
   "ip"              = "192.168.2.39/24"
   "local_as"        = "64539"
},
{
   "hostname"        = "worker-37"
   "ip"              = "192.168.2.40/24"
   "local_as"        = "64540"
},
{
   "hostname"        = "worker-38"
   "ip"              = "192.168.2.41/24"
   "local_as"        = "64541"
},
{
   "hostname"        = "worker-39"
   "ip"              = "192.168.2.42/24"
   "local_as"        = "64542"
},
{
   "hostname"        = "worker-40"
   "ip"              = "192.168.2.43/24"
   "local_as"        = "64543"
},
{
   "hostname"        = "worker-41"
   "ip"              = "192.168.2.44/24"
   "local_as"        = "64544"
},
{
   "hostname"        = "worker-42"
   "ip"              = "192.168.2.45/24"
   "local_as"        = "64545"
},
{
   "hostname"        = "worker-43"
   "ip"              = "192.168.2.46/24"
   "local_as"        = "64546"
},
{
   "hostname"        = "worker-44"
   "ip"              = "192.168.2.47/24"
   "local_as"        = "64547"
},
{
   "hostname"        = "worker-45"
   "ip"              = "192.168.2.48/24"
   "local_as"        = "64548"
},
{
   "hostname"        = "worker-46"
   "ip"              = "192.168.2.49/24"
   "local_as"        = "64549"
},
{
   "hostname"        = "worker-47"
   "ip"              = "192.168.2.50/24"
   "local_as"        = "64550"
},
{
   "hostname"        = "worker-48"
   "ip"              = "192.168.2.51/24"
   "local_as"        = "64551"
},
{
   "hostname"        = "worker-49"
   "ip"              = "192.168.2.52/24"
   "local_as"        = "64552"
},
{
   "hostname"        = "worker-50"
   "ip"              = "192.168.2.53/24"
   "local_as"        = "64553"
},
{
   "hostname"        = "worker-51"
   "ip"              = "192.168.2.54/24"
   "local_as"        = "64554"
},
{
   "hostname"        = "worker-52"
   "ip"              = "192.168.2.55/24"
   "local_as"        = "64555"
},
{
   "hostname"        = "worker-53"
   "ip"              = "192.168.2.56/24"
   "local_as"        = "64556"
},
{
   "hostname"        = "worker-54"
   "ip"              = "192.168.2.57/24"
   "local_as"        = "64557"
},
{
   "hostname"        = "worker-55"
   "ip"              = "192.168.2.58/24"
   "local_as"        = "64558"
},
{
   "hostname"        = "worker-56"
   "ip"              = "192.168.2.59/24"
   "local_as"        = "64559"
},
{
   "hostname"        = "worker-57"
   "ip"              = "192.168.2.60/24"
   "local_as"        = "64560"
},
{
   "hostname"        = "worker-58"
   "ip"              = "192.168.2.61/24"
   "local_as"        = "64561"
},
{
   "hostname"        = "worker-59"
   "ip"              = "192.168.2.62/24"
   "local_as"        = "64562"
},
{
   "hostname"        = "worker-60"
   "ip"              = "192.168.2.63/24"
   "local_as"        = "64563"
}
]

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