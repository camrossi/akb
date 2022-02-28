apic ={
    "username": "nkt_user_ocjqzw",
    "cert_name": "nkt_user_ocjqzw",
    "private_key": "../ansible/roles/aci/files/nkt_user_ocjqzw-user.key",
    "url": "https://10.67.185.102",
    "oob_ips": "10.67.185.102,10.67.185.41,10.67.185.42"
}
l3out ={
    "name": "CalicoL3OUT",
    "l3out_tenant": "calico2",
    "vrf_tenant": "calico2",
    "vrf_name": "vrf",
    "node_profile_name": "node_profile_FL3out",
    "int_prof_name": "int_profile_FL3out",
    "int_prof_name_v6": "int_profile_v6_FL3out",
    "physical_dom": "Fab2",
    "floating_ipv6": "2001:db8:12:ff:ffff:ffff:ffff:fffe/56",
    "secondary_ipv6": "2001:db8:12:ff:ffff:ffff:ffff:fffd/56",
    "floating_ip": "192.168.12.254/24",
    "secondary_ip": "192.168.12.253/24",
    "def_ext_epg": "catch_all",
    "def_ext_epg_scope": [
        "import-security",
        "shared-rtctrl",
        "shared-security"
    ],
    "local_as": "65002",
    "mtu": "9000",
    "bgp_pass": "123Cisco123",
    "max_node_prefixes": "500",
    "contract": "calico2",
    "contract_tenant": "common",
    "dns_servers": [
        "10.67.185.100"
    ],
    "dns_domain": "cam.ciscolabs.com",
    "anchor_nodes": [
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "201",
            "rtr_id": "1.1.1.201",
            "primary_ip": "192.168.12.201/24",
            "primary_ipv6": "2001:db8:12::201/56"
        },
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "202",
            "rtr_id": "1.1.1.202",
            "primary_ip": "192.168.12.202/24",
            "primary_ipv6": "2001:db8:12::202/56"
        },
        {
            "pod_id": "1",
            "rack_id": "2",
            "node_id": "203",
            "rtr_id": "1.1.1.203",
            "primary_ip": "192.168.12.203/24",
            "primary_ipv6": "2001:db8:12::203/56"
        },
        {
            "pod_id": "1",
            "rack_id": "2",
            "node_id": "204",
            "rtr_id": "1.1.1.204",
            "primary_ip": "192.168.12.204/24",
            "primary_ipv6": "2001:db8:12::204/56"
        }
    ],
    "ipv4_cluster_subnet": "192.168.12.0/24",
    "ipv6_cluster_subnet": "2001:db8:12::/56",
    "ipv6_enabled": true,
    "vlan_id": "310"
}
calico_nodes =[
{
    "hostname"        : "calico-1",
    "ip"              : "192.168.12.1/24",
    "ipv6"            : "2001:db8:12::1/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-2",
    "ip"              : "192.168.12.2/24",
    "ipv6"            : "2001:db8:12::2/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-3",
    "ip"              : "192.168.12.3/24",
    "ipv6"            : "2001:db8:12::3/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-4",
    "ip"              : "192.168.12.4/24",
    "ipv6"            : "2001:db8:12::4/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-5",
    "ip"              : "192.168.12.5/24",
    "ipv6"            : "2001:db8:12::5/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-6",
    "ip"              : "192.168.12.6/24",
    "ipv6"            : "2001:db8:12::6/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-7",
    "ip"              : "192.168.12.7/24",
    "ipv6"            : "2001:db8:12::7/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-8",
    "ip"              : "192.168.12.8/24",
    "ipv6"            : "2001:db8:12::8/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-9",
    "ip"              : "192.168.12.9/24",
    "ipv6"            : "2001:db8:12::9/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-10",
    "ip"              : "192.168.12.10/24",
    "ipv6"            : "2001:db8:12::a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-11",
    "ip"              : "192.168.12.11/24",
    "ipv6"            : "2001:db8:12::b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-12",
    "ip"              : "192.168.12.12/24",
    "ipv6"            : "2001:db8:12::c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-13",
    "ip"              : "192.168.12.13/24",
    "ipv6"            : "2001:db8:12::d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-14",
    "ip"              : "192.168.12.14/24",
    "ipv6"            : "2001:db8:12::e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-15",
    "ip"              : "192.168.12.15/24",
    "ipv6"            : "2001:db8:12::f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-16",
    "ip"              : "192.168.12.16/24",
    "ipv6"            : "2001:db8:12::10/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-17",
    "ip"              : "192.168.12.17/24",
    "ipv6"            : "2001:db8:12::11/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-18",
    "ip"              : "192.168.12.18/24",
    "ipv6"            : "2001:db8:12::12/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-19",
    "ip"              : "192.168.12.19/24",
    "ipv6"            : "2001:db8:12::13/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-20",
    "ip"              : "192.168.12.20/24",
    "ipv6"            : "2001:db8:12::14/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-21",
    "ip"              : "192.168.12.21/24",
    "ipv6"            : "2001:db8:12::15/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-22",
    "ip"              : "192.168.12.22/24",
    "ipv6"            : "2001:db8:12::16/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-23",
    "ip"              : "192.168.12.23/24",
    "ipv6"            : "2001:db8:12::17/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-24",
    "ip"              : "192.168.12.24/24",
    "ipv6"            : "2001:db8:12::18/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-25",
    "ip"              : "192.168.12.25/24",
    "ipv6"            : "2001:db8:12::19/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-26",
    "ip"              : "192.168.12.26/24",
    "ipv6"            : "2001:db8:12::1a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-27",
    "ip"              : "192.168.12.27/24",
    "ipv6"            : "2001:db8:12::1b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-28",
    "ip"              : "192.168.12.28/24",
    "ipv6"            : "2001:db8:12::1c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-29",
    "ip"              : "192.168.12.29/24",
    "ipv6"            : "2001:db8:12::1d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-30",
    "ip"              : "192.168.12.30/24",
    "ipv6"            : "2001:db8:12::1e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-31",
    "ip"              : "192.168.12.31/24",
    "ipv6"            : "2001:db8:12::1f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-32",
    "ip"              : "192.168.12.32/24",
    "ipv6"            : "2001:db8:12::20/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-33",
    "ip"              : "192.168.12.33/24",
    "ipv6"            : "2001:db8:12::21/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-34",
    "ip"              : "192.168.12.34/24",
    "ipv6"            : "2001:db8:12::22/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-35",
    "ip"              : "192.168.12.35/24",
    "ipv6"            : "2001:db8:12::23/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-36",
    "ip"              : "192.168.12.36/24",
    "ipv6"            : "2001:db8:12::24/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-37",
    "ip"              : "192.168.12.37/24",
    "ipv6"            : "2001:db8:12::25/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-38",
    "ip"              : "192.168.12.38/24",
    "ipv6"            : "2001:db8:12::26/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-39",
    "ip"              : "192.168.12.39/24",
    "ipv6"            : "2001:db8:12::27/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-40",
    "ip"              : "192.168.12.40/24",
    "ipv6"            : "2001:db8:12::28/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-41",
    "ip"              : "192.168.12.41/24",
    "ipv6"            : "2001:db8:12::29/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-42",
    "ip"              : "192.168.12.42/24",
    "ipv6"            : "2001:db8:12::2a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-43",
    "ip"              : "192.168.12.43/24",
    "ipv6"            : "2001:db8:12::2b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-44",
    "ip"              : "192.168.12.44/24",
    "ipv6"            : "2001:db8:12::2c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-45",
    "ip"              : "192.168.12.45/24",
    "ipv6"            : "2001:db8:12::2d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-46",
    "ip"              : "192.168.12.46/24",
    "ipv6"            : "2001:db8:12::2e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-47",
    "ip"              : "192.168.12.47/24",
    "ipv6"            : "2001:db8:12::2f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-48",
    "ip"              : "192.168.12.48/24",
    "ipv6"            : "2001:db8:12::30/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-49",
    "ip"              : "192.168.12.49/24",
    "ipv6"            : "2001:db8:12::31/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-50",
    "ip"              : "192.168.12.50/24",
    "ipv6"            : "2001:db8:12::32/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-51",
    "ip"              : "192.168.12.51/24",
    "ipv6"            : "2001:db8:12::33/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-52",
    "ip"              : "192.168.12.52/24",
    "ipv6"            : "2001:db8:12::34/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-53",
    "ip"              : "192.168.12.53/24",
    "ipv6"            : "2001:db8:12::35/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-54",
    "ip"              : "192.168.12.54/24",
    "ipv6"            : "2001:db8:12::36/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-55",
    "ip"              : "192.168.12.55/24",
    "ipv6"            : "2001:db8:12::37/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-56",
    "ip"              : "192.168.12.56/24",
    "ipv6"            : "2001:db8:12::38/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-57",
    "ip"              : "192.168.12.57/24",
    "ipv6"            : "2001:db8:12::39/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-58",
    "ip"              : "192.168.12.58/24",
    "ipv6"            : "2001:db8:12::3a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-59",
    "ip"              : "192.168.12.59/24",
    "ipv6"            : "2001:db8:12::3b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-60",
    "ip"              : "192.168.12.60/24",
    "ipv6"            : "2001:db8:12::3c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-61",
    "ip"              : "192.168.12.61/24",
    "ipv6"            : "2001:db8:12::3d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-62",
    "ip"              : "192.168.12.62/24",
    "ipv6"            : "2001:db8:12::3e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-63",
    "ip"              : "192.168.12.63/24",
    "ipv6"            : "2001:db8:12::3f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-64",
    "ip"              : "192.168.12.64/24",
    "ipv6"            : "2001:db8:12::40/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-65",
    "ip"              : "192.168.12.65/24",
    "ipv6"            : "2001:db8:12::41/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-66",
    "ip"              : "192.168.12.66/24",
    "ipv6"            : "2001:db8:12::42/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-67",
    "ip"              : "192.168.12.67/24",
    "ipv6"            : "2001:db8:12::43/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-68",
    "ip"              : "192.168.12.68/24",
    "ipv6"            : "2001:db8:12::44/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-69",
    "ip"              : "192.168.12.69/24",
    "ipv6"            : "2001:db8:12::45/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-70",
    "ip"              : "192.168.12.70/24",
    "ipv6"            : "2001:db8:12::46/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-71",
    "ip"              : "192.168.12.71/24",
    "ipv6"            : "2001:db8:12::47/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-72",
    "ip"              : "192.168.12.72/24",
    "ipv6"            : "2001:db8:12::48/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-73",
    "ip"              : "192.168.12.73/24",
    "ipv6"            : "2001:db8:12::49/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-74",
    "ip"              : "192.168.12.74/24",
    "ipv6"            : "2001:db8:12::4a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-75",
    "ip"              : "192.168.12.75/24",
    "ipv6"            : "2001:db8:12::4b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-76",
    "ip"              : "192.168.12.76/24",
    "ipv6"            : "2001:db8:12::4c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-77",
    "ip"              : "192.168.12.77/24",
    "ipv6"            : "2001:db8:12::4d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-78",
    "ip"              : "192.168.12.78/24",
    "ipv6"            : "2001:db8:12::4e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-79",
    "ip"              : "192.168.12.79/24",
    "ipv6"            : "2001:db8:12::4f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-80",
    "ip"              : "192.168.12.80/24",
    "ipv6"            : "2001:db8:12::50/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-81",
    "ip"              : "192.168.12.81/24",
    "ipv6"            : "2001:db8:12::51/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-82",
    "ip"              : "192.168.12.82/24",
    "ipv6"            : "2001:db8:12::52/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-83",
    "ip"              : "192.168.12.83/24",
    "ipv6"            : "2001:db8:12::53/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-84",
    "ip"              : "192.168.12.84/24",
    "ipv6"            : "2001:db8:12::54/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-85",
    "ip"              : "192.168.12.85/24",
    "ipv6"            : "2001:db8:12::55/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-86",
    "ip"              : "192.168.12.86/24",
    "ipv6"            : "2001:db8:12::56/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-87",
    "ip"              : "192.168.12.87/24",
    "ipv6"            : "2001:db8:12::57/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-88",
    "ip"              : "192.168.12.88/24",
    "ipv6"            : "2001:db8:12::58/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-89",
    "ip"              : "192.168.12.89/24",
    "ipv6"            : "2001:db8:12::59/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-90",
    "ip"              : "192.168.12.90/24",
    "ipv6"            : "2001:db8:12::5a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-91",
    "ip"              : "192.168.12.91/24",
    "ipv6"            : "2001:db8:12::5b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-92",
    "ip"              : "192.168.12.92/24",
    "ipv6"            : "2001:db8:12::5c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-93",
    "ip"              : "192.168.12.93/24",
    "ipv6"            : "2001:db8:12::5d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-94",
    "ip"              : "192.168.12.94/24",
    "ipv6"            : "2001:db8:12::5e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-95",
    "ip"              : "192.168.12.95/24",
    "ipv6"            : "2001:db8:12::5f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-96",
    "ip"              : "192.168.12.96/24",
    "ipv6"            : "2001:db8:12::60/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-97",
    "ip"              : "192.168.12.97/24",
    "ipv6"            : "2001:db8:12::61/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-98",
    "ip"              : "192.168.12.98/24",
    "ipv6"            : "2001:db8:12::62/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-99",
    "ip"              : "192.168.12.99/24",
    "ipv6"            : "2001:db8:12::63/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-100",
    "ip"              : "192.168.12.100/24",
    "ipv6"            : "2001:db8:12::64/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-101",
    "ip"              : "192.168.12.101/24",
    "ipv6"            : "2001:db8:12::65/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-102",
    "ip"              : "192.168.12.102/24",
    "ipv6"            : "2001:db8:12::66/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-103",
    "ip"              : "192.168.12.103/24",
    "ipv6"            : "2001:db8:12::67/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-104",
    "ip"              : "192.168.12.104/24",
    "ipv6"            : "2001:db8:12::68/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-105",
    "ip"              : "192.168.12.105/24",
    "ipv6"            : "2001:db8:12::69/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-106",
    "ip"              : "192.168.12.106/24",
    "ipv6"            : "2001:db8:12::6a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-107",
    "ip"              : "192.168.12.107/24",
    "ipv6"            : "2001:db8:12::6b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-108",
    "ip"              : "192.168.12.108/24",
    "ipv6"            : "2001:db8:12::6c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-109",
    "ip"              : "192.168.12.109/24",
    "ipv6"            : "2001:db8:12::6d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-110",
    "ip"              : "192.168.12.110/24",
    "ipv6"            : "2001:db8:12::6e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-111",
    "ip"              : "192.168.12.111/24",
    "ipv6"            : "2001:db8:12::6f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-112",
    "ip"              : "192.168.12.112/24",
    "ipv6"            : "2001:db8:12::70/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-113",
    "ip"              : "192.168.12.113/24",
    "ipv6"            : "2001:db8:12::71/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-114",
    "ip"              : "192.168.12.114/24",
    "ipv6"            : "2001:db8:12::72/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-115",
    "ip"              : "192.168.12.115/24",
    "ipv6"            : "2001:db8:12::73/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-116",
    "ip"              : "192.168.12.116/24",
    "ipv6"            : "2001:db8:12::74/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-117",
    "ip"              : "192.168.12.117/24",
    "ipv6"            : "2001:db8:12::75/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-118",
    "ip"              : "192.168.12.118/24",
    "ipv6"            : "2001:db8:12::76/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-119",
    "ip"              : "192.168.12.119/24",
    "ipv6"            : "2001:db8:12::77/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-120",
    "ip"              : "192.168.12.120/24",
    "ipv6"            : "2001:db8:12::78/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-121",
    "ip"              : "192.168.12.121/24",
    "ipv6"            : "2001:db8:12::79/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-122",
    "ip"              : "192.168.12.122/24",
    "ipv6"            : "2001:db8:12::7a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-123",
    "ip"              : "192.168.12.123/24",
    "ipv6"            : "2001:db8:12::7b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-124",
    "ip"              : "192.168.12.124/24",
    "ipv6"            : "2001:db8:12::7c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-125",
    "ip"              : "192.168.12.125/24",
    "ipv6"            : "2001:db8:12::7d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-126",
    "ip"              : "192.168.12.126/24",
    "ipv6"            : "2001:db8:12::7e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-127",
    "ip"              : "192.168.12.127/24",
    "ipv6"            : "2001:db8:12::7f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-128",
    "ip"              : "192.168.12.128/24",
    "ipv6"            : "2001:db8:12::80/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-129",
    "ip"              : "192.168.12.129/24",
    "ipv6"            : "2001:db8:12::81/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-130",
    "ip"              : "192.168.12.130/24",
    "ipv6"            : "2001:db8:12::82/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-131",
    "ip"              : "192.168.12.131/24",
    "ipv6"            : "2001:db8:12::83/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-132",
    "ip"              : "192.168.12.132/24",
    "ipv6"            : "2001:db8:12::84/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-133",
    "ip"              : "192.168.12.133/24",
    "ipv6"            : "2001:db8:12::85/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-134",
    "ip"              : "192.168.12.134/24",
    "ipv6"            : "2001:db8:12::86/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-135",
    "ip"              : "192.168.12.135/24",
    "ipv6"            : "2001:db8:12::87/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-136",
    "ip"              : "192.168.12.136/24",
    "ipv6"            : "2001:db8:12::88/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-137",
    "ip"              : "192.168.12.137/24",
    "ipv6"            : "2001:db8:12::89/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-138",
    "ip"              : "192.168.12.138/24",
    "ipv6"            : "2001:db8:12::8a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-139",
    "ip"              : "192.168.12.139/24",
    "ipv6"            : "2001:db8:12::8b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-140",
    "ip"              : "192.168.12.140/24",
    "ipv6"            : "2001:db8:12::8c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-141",
    "ip"              : "192.168.12.141/24",
    "ipv6"            : "2001:db8:12::8d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-142",
    "ip"              : "192.168.12.142/24",
    "ipv6"            : "2001:db8:12::8e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-143",
    "ip"              : "192.168.12.143/24",
    "ipv6"            : "2001:db8:12::8f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-144",
    "ip"              : "192.168.12.144/24",
    "ipv6"            : "2001:db8:12::90/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-145",
    "ip"              : "192.168.12.145/24",
    "ipv6"            : "2001:db8:12::91/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-146",
    "ip"              : "192.168.12.146/24",
    "ipv6"            : "2001:db8:12::92/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-147",
    "ip"              : "192.168.12.147/24",
    "ipv6"            : "2001:db8:12::93/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-148",
    "ip"              : "192.168.12.148/24",
    "ipv6"            : "2001:db8:12::94/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-149",
    "ip"              : "192.168.12.149/24",
    "ipv6"            : "2001:db8:12::95/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-150",
    "ip"              : "192.168.12.150/24",
    "ipv6"            : "2001:db8:12::96/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-151",
    "ip"              : "192.168.12.151/24",
    "ipv6"            : "2001:db8:12::97/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-152",
    "ip"              : "192.168.12.152/24",
    "ipv6"            : "2001:db8:12::98/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-153",
    "ip"              : "192.168.12.153/24",
    "ipv6"            : "2001:db8:12::99/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-154",
    "ip"              : "192.168.12.154/24",
    "ipv6"            : "2001:db8:12::9a/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-155",
    "ip"              : "192.168.12.155/24",
    "ipv6"            : "2001:db8:12::9b/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-156",
    "ip"              : "192.168.12.156/24",
    "ipv6"            : "2001:db8:12::9c/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-157",
    "ip"              : "192.168.12.157/24",
    "ipv6"            : "2001:db8:12::9d/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-158",
    "ip"              : "192.168.12.158/24",
    "ipv6"            : "2001:db8:12::9e/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-159",
    "ip"              : "192.168.12.159/24",
    "ipv6"            : "2001:db8:12::9f/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-160",
    "ip"              : "192.168.12.160/24",
    "ipv6"            : "2001:db8:12::a0/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-161",
    "ip"              : "192.168.12.161/24",
    "ipv6"            : "2001:db8:12::a1/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-162",
    "ip"              : "192.168.12.162/24",
    "ipv6"            : "2001:db8:12::a2/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-163",
    "ip"              : "192.168.12.163/24",
    "ipv6"            : "2001:db8:12::a3/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-164",
    "ip"              : "192.168.12.164/24",
    "ipv6"            : "2001:db8:12::a4/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-165",
    "ip"              : "192.168.12.165/24",
    "ipv6"            : "2001:db8:12::a5/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-166",
    "ip"              : "192.168.12.166/24",
    "ipv6"            : "2001:db8:12::a6/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-167",
    "ip"              : "192.168.12.167/24",
    "ipv6"            : "2001:db8:12::a7/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-168",
    "ip"              : "192.168.12.168/24",
    "ipv6"            : "2001:db8:12::a8/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-169",
    "ip"              : "192.168.12.169/24",
    "ipv6"            : "2001:db8:12::a9/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-170",
    "ip"              : "192.168.12.170/24",
    "ipv6"            : "2001:db8:12::aa/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-171",
    "ip"              : "192.168.12.171/24",
    "ipv6"            : "2001:db8:12::ab/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-172",
    "ip"              : "192.168.12.172/24",
    "ipv6"            : "2001:db8:12::ac/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-173",
    "ip"              : "192.168.12.173/24",
    "ipv6"            : "2001:db8:12::ad/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-174",
    "ip"              : "192.168.12.174/24",
    "ipv6"            : "2001:db8:12::ae/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-175",
    "ip"              : "192.168.12.175/24",
    "ipv6"            : "2001:db8:12::af/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-176",
    "ip"              : "192.168.12.176/24",
    "ipv6"            : "2001:db8:12::b0/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-177",
    "ip"              : "192.168.12.177/24",
    "ipv6"            : "2001:db8:12::b1/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-178",
    "ip"              : "192.168.12.178/24",
    "ipv6"            : "2001:db8:12::b2/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-179",
    "ip"              : "192.168.12.179/24",
    "ipv6"            : "2001:db8:12::b3/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-180",
    "ip"              : "192.168.12.180/24",
    "ipv6"            : "2001:db8:12::b4/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-181",
    "ip"              : "192.168.12.181/24",
    "ipv6"            : "2001:db8:12::b5/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-182",
    "ip"              : "192.168.12.182/24",
    "ipv6"            : "2001:db8:12::b6/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-183",
    "ip"              : "192.168.12.183/24",
    "ipv6"            : "2001:db8:12::b7/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-184",
    "ip"              : "192.168.12.184/24",
    "ipv6"            : "2001:db8:12::b8/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-185",
    "ip"              : "192.168.12.185/24",
    "ipv6"            : "2001:db8:12::b9/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-186",
    "ip"              : "192.168.12.186/24",
    "ipv6"            : "2001:db8:12::ba/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-187",
    "ip"              : "192.168.12.187/24",
    "ipv6"            : "2001:db8:12::bb/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-188",
    "ip"              : "192.168.12.188/24",
    "ipv6"            : "2001:db8:12::bc/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-189",
    "ip"              : "192.168.12.189/24",
    "ipv6"            : "2001:db8:12::bd/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-190",
    "ip"              : "192.168.12.190/24",
    "ipv6"            : "2001:db8:12::be/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-191",
    "ip"              : "192.168.12.191/24",
    "ipv6"            : "2001:db8:12::bf/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-192",
    "ip"              : "192.168.12.192/24",
    "ipv6"            : "2001:db8:12::c0/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-193",
    "ip"              : "192.168.12.193/24",
    "ipv6"            : "2001:db8:12::c1/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-194",
    "ip"              : "192.168.12.194/24",
    "ipv6"            : "2001:db8:12::c2/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-195",
    "ip"              : "192.168.12.195/24",
    "ipv6"            : "2001:db8:12::c3/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-196",
    "ip"              : "192.168.12.196/24",
    "ipv6"            : "2001:db8:12::c4/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-197",
    "ip"              : "192.168.12.197/24",
    "ipv6"            : "2001:db8:12::c5/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-198",
    "ip"              : "192.168.12.198/24",
    "ipv6"            : "2001:db8:12::c6/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
},
{
    "hostname"        : "calico-199",
    "ip"              : "192.168.12.199/24",
    "ipv6"            : "2001:db8:12::c7/56",
    "local_as"        : "650011",
    "rack_id"         : "2",
    "natip"           : ""
},
{
    "hostname"        : "calico-200",
    "ip"              : "192.168.12.200/24",
    "ipv6"            : "2001:db8:12::c8/56",
    "local_as"        : "650011",
    "rack_id"         : "1",
    "natip"           : ""
}
]
vc ={
    "url": "vc2.cam.ciscolabs.com",
    "username": "administrator@vsphere.local",
    "pass": "123Cisco123!",
    "dc": "STLD",
    "datastore": "BM01",
    "cluster": "Cluster",
    "dvs": "ACI",
    "port_group": "CalicoL3OUT-310",
    "vm_template": "nkt_template",
    "vm_folder": "AlpineVMs",
    "vm_deploy": true
}
k8s_cluster ={
    "control_plane_vip": "192.168.12.252",
    "vip_port": "8443",
    "pod_subnet": "192.168.13.0/24",
    "pod_subnet_v6": "2001:db8:12:100::/56",
    "cluster_svc_subnet": "192.168.14.0/24",
    "cluster_svc_subnet_v6": "2001:db8:12:200::/108",
    "external_svc_subnet": "192.168.15.0/24",
    "external_svc_subnet_v6": "2001:db8:12:200::10:0/108",
    "local_as": "65002",
    "ingress_ip": "192.168.15.1",
    "visibility_ip": "192.168.15.2",
    "neo4j_ip": "192.168.15.3",
    "kubeadm_token": "fqv728.htdmfzf6rt9blhej",
    "node_sub": "192.168.12.0/24",
    "node_sub_v6": "2001:db8:12::/56",
    "ntp_server": "72.163.32.44",
    "kube_version": "1.23.4-00",
    "crio_version": "1.23",
    "OS_Version": "xUbuntu_21.04",
    "haproxy_image": "haproxy:latest",
    "keepalived_image": "osixia/keepalived:latest",
    "keepalived_router_id": "51",
    "time_zone": "Australia/Sydney",
    "docker_mirror": "10.67.185.120:5000",
    "http_proxy_status": "",
    "http_proxy": "",
    "ubuntu_apt_mirror": "",
    "sandbox_status": true
}