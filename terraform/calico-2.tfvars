apic ={
    "url": "https://10.67.185.102",
    "username": "ansible",
    "cert_name": "ansible.crt",
    "private_key": "/home/cisco/Coding/ansible.key"
    "oob_ips": "10.67.185.102,10.67.185.41,10.67.185.42"
}
vc ={
    "url": "vc2.cam.ciscolabs.com",
    "username": "administrator@vsphere.local",
    "pass": "123Cisco123!",
    "dc": "STLD",
    "datastore": "BM01",
    "cluster": "Cluster",kubeadm_token
    "dvs": "ACI",
    "port_group": "CalicoL3OUT-310",
    "vm_template": "Ubuntu21SandBox",
    "vm_folder": "Calico-Cluster2"
}
l3out ={
    "ipv4_cluster_subnet": "192.168.12.0/24",
    "ipv6_cluster_subnet": "2001:db8:12::0/56",
    "ipv6_enabled": true,
    "vlan_id": "310",
    "name": "calico_l3out",
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
    ]

}
calico_nodes =[
    {
        "hostname"        : "calico-1",
        "ip"              : "192.168.12.1/24",
        "ipv6"            : "2001:db8:12::1/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-2",
        "ip"              : "192.168.12.2/24",
        "ipv6"            : "2001:db8:12::2/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-3",
        "ip"              : "192.168.12.3/24",
        "ipv6"            : "2001:db8:12::3/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-4",
        "ip"              : "192.168.12.4/24",
        "ipv6"            : "2001:db8:12::4/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-5",
        "ip"              : "192.168.12.5/24",
        "ipv6"            : "2001:db8:12::5/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-6",
        "ip"              : "192.168.12.6/24",
        "ipv6"            : "2001:db8:12::6/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-7",
        "ip"              : "192.168.12.7/24",
        "ipv6"            : "2001:db8:12::7/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-8",
        "ip"              : "192.168.12.8/24",
        "ipv6"            : "2001:db8:12::8/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-9",
        "ip"              : "192.168.12.9/24",
        "ipv6"            : "2001:db8:12::9/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-10",
        "ip"              : "192.168.12.10/24",
        "ipv6"            : "2001:db8:12::a/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-11",
        "ip"              : "192.168.12.11/24",
        "ipv6"            : "2001:db8:12::b/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-12",
        "ip"              : "192.168.12.12/24",
        "ipv6"            : "2001:db8:12::c/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-13",
        "ip"              : "192.168.12.13/24",
        "ipv6"            : "2001:db8:12::d/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-14",
        "ip"              : "192.168.12.14/24",
        "ipv6"            : "2001:db8:12::e/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-15",
        "ip"              : "192.168.12.15/24",
        "ipv6"            : "2001:db8:12::f/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-16",
        "ip"              : "192.168.12.16/24",
        "ipv6"            : "2001:db8:12::10/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-17",
        "ip"              : "192.168.12.17/24",
        "ipv6"            : "2001:db8:12::11/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-18",
        "ip"              : "192.168.12.18/24",
        "ipv6"            : "2001:db8:12::12/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-19",
        "ip"              : "192.168.12.19/24",
        "ipv6"            : "2001:db8:12::13/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-20",
        "ip"              : "192.168.12.20/24",
        "ipv6"            : "2001:db8:12::14/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-21",
        "ip"              : "192.168.12.21/24",
        "ipv6"            : "2001:db8:12::15/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-22",
        "ip"              : "192.168.12.22/24",
        "ipv6"            : "2001:db8:12::16/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-23",
        "ip"              : "192.168.12.23/24",
        "ipv6"            : "2001:db8:12::17/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-24",
        "ip"              : "192.168.12.24/24",
        "ipv6"            : "2001:db8:12::18/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-25",
        "ip"              : "192.168.12.25/24",
        "ipv6"            : "2001:db8:12::19/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-26",
        "ip"              : "192.168.12.26/24",
        "ipv6"            : "2001:db8:12::1a/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-27",
        "ip"              : "192.168.12.27/24",
        "ipv6"            : "2001:db8:12::1b/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-28",
        "ip"              : "192.168.12.28/24",
        "ipv6"            : "2001:db8:12::1c/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-29",
        "ip"              : "192.168.12.29/24",
        "ipv6"            : "2001:db8:12::1d/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-30",
        "ip"              : "192.168.12.30/24",
        "ipv6"            : "2001:db8:12::1e/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-31",
        "ip"              : "192.168.12.31/24",
        "ipv6"            : "2001:db8:12::1f/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-32",
        "ip"              : "192.168.12.32/24",
        "ipv6"            : "2001:db8:12::20/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-33",
        "ip"              : "192.168.12.33/24",
        "ipv6"            : "2001:db8:12::21/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-34",
        "ip"              : "192.168.12.34/24",
        "ipv6"            : "2001:db8:12::22/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-35",
        "ip"              : "192.168.12.35/24",
        "ipv6"            : "2001:db8:12::23/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-36",
        "ip"              : "192.168.12.36/24",
        "ipv6"            : "2001:db8:12::24/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-37",
        "ip"              : "192.168.12.37/24",
        "ipv6"            : "2001:db8:12::25/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-38",
        "ip"              : "192.168.12.38/24",
        "ipv6"            : "2001:db8:12::26/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-39",
        "ip"              : "192.168.12.39/24",
        "ipv6"            : "2001:db8:12::27/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-40",
        "ip"              : "192.168.12.40/24",
        "ipv6"            : "2001:db8:12::28/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-41",
        "ip"              : "192.168.12.41/24",
        "ipv6"            : "2001:db8:12::29/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-42",
        "ip"              : "192.168.12.42/24",
        "ipv6"            : "2001:db8:12::2a/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-43",
        "ip"              : "192.168.12.43/24",
        "ipv6"            : "2001:db8:12::2b/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-44",
        "ip"              : "192.168.12.44/24",
        "ipv6"            : "2001:db8:12::2c/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-45",
        "ip"              : "192.168.12.45/24",
        "ipv6"            : "2001:db8:12::2d/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-46",
        "ip"              : "192.168.12.46/24",
        "ipv6"            : "2001:db8:12::2e/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-47",
        "ip"              : "192.168.12.47/24",
        "ipv6"            : "2001:db8:12::2f/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-48",
        "ip"              : "192.168.12.48/24",
        "ipv6"            : "2001:db8:12::30/56",
        "rack_id"         : "1",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-49",
        "ip"              : "192.168.12.49/24",
        "ipv6"            : "2001:db8:12::31/56",
        "rack_id"         : "2",
        "natip"           : ""
    },
    {
        "hostname"        : "calico-50",
        "ip"              : "192.168.12.50/24",
        "ipv6"            : "2001:db8:12::32/56",
        "rack_id"         : "1",
        "natip"           : ""
    }
]
k8s_cluster ={
    "local_as": "65011",
    "control_plane_vip": "192.168.12.252",
    "vip_port": "8443",
    "pod_subnet": "192.168.16.0/22",
    "pod_subnet_v6": "2001:db8:12:100::/56",
    "cluster_svc_subnet": "192.168.14.0/24",
    "cluster_svc_subnet_v6": "2001:db8:12:200::/112",
    "external_svc_subnet": "192.168.15.0/24",
    "external_svc_subnet_v6": "2001:db8:12:300::/112",
    "ingress_ip": "192.168.15.1",
    "kubeadm_token": "fqv728.htdmfzf6rt9blhej",
    "node_sub": "192.168.12.0/24",
    "node_sub_v6": "2001:db8:12::0/56",
    "ntp_server": "72.163.32.44",
    "kube_version": "1.23.3-00",
    "crio_version": "1.23",
    "OS_Version": "xUbuntu_21.04",
    "haproxy_image": "haproxy:latest",
    "keepalived_image": "osixia/keepalived:latest",
    "keepalived_router_id": "51",
    "time_zone": "Australia/Sydney",
    "docker_mirror": "10.67.185.120:5000",
    "http_proxy_status": "",
    "http_proxy": "",
    "sandbox_status": true,
    "ubuntu_apt_mirror": "ubuntu.mirror.digitalpacific.com.au/archive/"
    
}