apic_username = "admin"
apic_password = "123Cisco123"
apic_url = "http://fab2-apic1.cam.ciscolabs.com"

l3out = {
    name                = "calico_l3out"
    l3out_tenant        = "common"
    vrf_tenant          = "common"
    vrf_name            = "calico"
    node_profile_name   = "NodePfl"
    int_prof_name       = "FloatingSVI"
    def_ext_epg         = "catch_all"
    anchor_nodes = [
        {
        node_id         = 201
        pod_id          = 1
        rtr_id          = "1.1.4.201"
        primary_ip      = "192.168.1.201/24"
        },
        {
        node_id         = 202
        pod_id          = 1
        rtr_id          = "1.1.4.202"
        primary_ip      = "192.168.1.202/24"
        }
    ]
    physical_dom        = "Fab2"
    secondary_ip        = "192.168.1.254/24"
    floating_ip         = "192.168.1.253/24"
    vlan_id             = 300     
}
