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
  port_group        = "CalicoL3OUT_301"
  vm_template       = "Ubuntu20-Template"
  vm_folder         = "Calico2.1"
}
dns_domain = "cam.ciscolabs.com"
dns_servers = ["10.67.185.100"]
l3out = {
    # Name of the L3OUT
    name                = "calico_l3out2" 
    # L3OUT could be in any tenant
    l3out_tenant        = "common"
    # VRF can be in common or in the same tenant as the l3out_tenant
    vrf_tenant          = "common"
    vrf_name            = "calico2"
    node_profile_name   = "NodePfl"
    int_prof_name       = "FloatingSVI"
    #For now I just use a catch all EPG with 0.0.0.0/0
    def_ext_epg         = "catch_all"
    def_ext_epg_scope   = ["import-security", "shared-security", "shared-rtctrl", ]
    # The Physcal domain: All ports mapped to this PhysDom will get programmed with VLAN_ID
    physical_dom        = "Fab2"
    # secondary_ip is the default GW for the calico nodes
    secondary_ip        = "192.168.12.254/24"
    # Used internally for leaf to leaf communicaiton. 
    floating_ip         = "192.168.12.253/24"
    # SVI VLAN ID
    vlan_id             = 301
    # The ACI AS must be the one configured as the ACI Route Reflectors. 
    local_as            = 65002
    contract            = "default1"
    # Anchor node list and configuration.
    anchor_nodes = [
        {
        node_id         = 201
        pod_id          = 1
        rtr_id          = "1.1.4.201"
        primary_ip      = "192.168.12.201/24"
        },
        {
        node_id         = 202
        pod_id          = 1
        rtr_id          = "1.1.4.202"
        primary_ip      = "192.168.12.202/24"
        }
    ]
}

# You MUST have 3 masters and N workers. 
# The 1st node is the primary master. 2nd and 3rd are the master replices and everything else is a worker.
# If you do not have 3 master the script will break...Need to make it more generic eventually
calico_nodes = [
        {
        hostname        = "master-1"
        ip              = "192.168.12.1/24"
        local_as        = 64501
        },
        {
        hostname        = "master-2"
        ip              = "192.168.12.2/24"
        local_as        = 64502
        },
        {
        hostname        = "master-3"
        ip              = "192.168.12.3/24"
        local_as        = 64503
        },
        {
        hostname        = "worker-1"
        ip              = "192.168.12.4/24"
        local_as        = 64504
        },
        {
        hostname        = "worker-2"
        ip              = "192.168.12.5/24"
        local_as        = 64505
        },
        {
        hostname        = "worker-3"
        ip              = "192.168.12.6/24"
        local_as        = 64506
        },
        {
        hostname        = "worker-4"
        ip              = "192.168.12.7/24"
        local_as        = 64507
        }
]

k8s_cluster = {
    kube_version        = "1.20.4-00"
    crio_version        = "1.20"
    OS_Version          = "xUbuntu_20.04"
    control_plane_vip   = "192.168.12.100"
    vip_port            = 8443
    haproxy_image       = "haproxy:2.3.6"
    keepalived_image    = "osixia/keepalived:2.0.20"
    keepalived_router_id= "51"
    kubeadm_token       = "fqv728.htdmfzf6rt9blhej"
    node_sub            = "192.168.12.0/24"
    pod_subnet          = "192.168.16.0/22"
    cluster_svc_subnet  = "192.168.20.0/22"
    ntp_server          = "72.163.32.44"
    time_zone           = "Australia/Sydney"
    docker_mirror       = "10.67.185.120:5000"
  }