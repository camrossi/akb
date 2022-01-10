apic ={
    "url": "https://10.67.185.102",
    "username": "ansible",
    "cert_name": "ansible.crt",
    "private_key": "/home/cisco/Coding/ansible.key"
}
vc ={
    "url": "vc2.cam.ciscolabs.com",
    "username": "administrator@vsphere.local",
    "pass": "123Cisco123!",
    "dc": "STLD",
    "datastore": "BM01",
    "cluster": "Cluster",
    "dvs": "ACI",
    "port_group": "CalicoL3OUT-310",
    "vm_template": "Ubuntu21-Template",
    "vm_folder": "Calico-Cluster2"
}
l3out ={
    "ipv4_cluster_subnet": "192.168.12.0/24",
    "ipv6_cluster_subnet": "2001:db8:12::0/56",
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
        "hostname": "calico-1",
        "ip": "192.168.12.11/24",
        "ipv6": "2001:db8:12::11/56",
        "natip": "",
        "local_as": "11",
        "rack_id": "1"
    },
    {
        "hostname": "calico-2",
        "ip": "192.168.12.12/24",
        "ipv6": "2001:db8:12::12/56",
        "natip": "",
        "local_as": "12",
        "rack_id": "1"
    },
    {
        "hostname": "calico-3",
        "ip": "192.168.12.13/24",
        "ipv6": "2001:db8:12::13/56",
        "natip": "",
        "local_as": "13",
        "rack_id": "2"
    },
    {
        "hostname": "calico-4",
        "ip": "192.168.12.14/24",
        "ipv6": "2001:db8:12::14/56",
        "natip": "",
        "local_as": "14",
        "rack_id": "2"
    }
]
k8s_cluster ={
    "control_plane_vip": "192.168.12.2",
    "vip_port": "8443",
    "pod_subnet": "192.168.13.0/24",
    "pod_subnet_v6": "2001:db8:12:100::/56",
    "cluster_svc_subnet": "192.168.14.0/24",
    "cluster_svc_subnet_v6": "2001:db8:12:200::/56",
    "external_svc_subnet": "192.168.15.0/24",
    "external_svc_subnet_v6": "2001:db8:12:300::/56",
    "ingress_ip": "192.168.15.1",
    "kubeadm_token": "fqv728.htdmfzf6rt9blhej",
    "node_sub": "192.168.12.0/24",
    "node_sub_v6": "2001:db8:12::0/56",
    "ntp_server": "72.163.32.44",
    "kube_version": "1.22.4-00",
    "crio_version": "1.22",
    "OS_Version": "xUbuntu_20.04",
    "haproxy_image": "haproxy:latest",
    "keepalived_image": "osixia/keepalived:latest",
    "keepalived_router_id": "51",
    "time_zone": "Australia/Sydney",
    "docker_mirror": "10.67.185.120:5000",
    "http_proxy_status": "",
    "http_proxy": ""
    
}