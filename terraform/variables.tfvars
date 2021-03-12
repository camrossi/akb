apic_username = "ansible"
apic_url = "http://fab2-apic1.cam.ciscolabs.com"
cert_name = "ansible.crt"
private_key = "/home/cisco/Coding/ansible.key"
vsphere_server = "vc2.cam.ciscolabs.com"
vsphere_user = "administrator@vsphere.local"
vsphere_password = "123Cisco123!"
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
    calico_node_sub  = "192.168.2.0/24"
    calico_pod_sub  = "192.168.3.0/24"
    calico_svc_sub  = "192.168.4.0/24"
    # The Physcal domain: All ports mapped to this PhysDom will get programmed with VLAN_ID
    physical_dom        = "Fab2"
    # secondary_ip is the default GW for the calico nodes
    secondary_ip        = "192.168.2.254/24"
    # Used internally for leaf to leaf communicaiton. 
    floating_ip         = "192.168.2.253/24"
    # SVI VLAN ID
    vlan_id             = 300
    local_as            = 64500
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

calico_nodes = [
        {
        hostname        = "master-1"
        ip              = "192.168.2.1/24"
        local_as        = 64501
        },
        {
        hostname        = "master-2"
        ip              = "192.168.2.2/24"
        local_as        = 64502
        },
        {
        hostname        = "master-3"
        ip              = "192.168.2.3/24"
        local_as        = 64503
        },
        {
        hostname        = "worker-1"
        ip              = "192.168.2.4/24"
        local_as        = 64504
        },
        {
        hostname        = "worker-2"
        ip              = "192.168.2.5/24"
        local_as        = 64505
        }
]
