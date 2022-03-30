apic ={
    "username": "nkt_user_fmgozn",
    "cert_name": "nkt_user_fmgozn",
    "private_key": "../ansible/roles/aci/files/nkt_user_fmgozn-user.key",
    "url": "https://10.48.170.201",
    "oob_ips": "10.48.170.201,10.48.170.203,10.48.170.202"
}
l3out ={
    "name": "CalicoL3OUT",
    "l3out_tenant": "common",
    "vrf_tenant": "common",
    "vrf_name": "k8sVRF2",
    "node_profile_name": "node_profile_FL3out",
    "int_prof_name": "int_profile_FL3out",
    "int_prof_name_v6": "int_profile_v6_FL3out",
    "physical_dom": "k8slab-pdom",
    "floating_ipv6": "",
    "secondary_ipv6": "",
    "floating_ip": "192.168.20.254/24",
    "secondary_ip": "192.168.20.253/24",
    "def_ext_epg": "catch_all",
    "def_ext_epg_scope": [
        "import-security",
        "shared-rtctrl",
        "shared-security"
    ],
    "local_as": "65534",
    "mtu": "9000",
    "bgp_pass": "123Cisco123",
    "max_node_prefixes": "500",
    "contract": "k8s",
    "contract_tenant": "common",
    "anchor_nodes": [
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "101",
            "rtr_id": "1.1.1.1",
            "ip": "192.168.20.101/24",
            "ipv6": ""
        },
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "102",
            "rtr_id": "1.1.1.2",
            "ip": "192.168.20.102/24",
            "ipv6": ""
        }
    ],
    "ipv4_cluster_subnet": "192.168.20.0/24",
    "ipv6_cluster_subnet": "",
    "ipv6_enabled": false,
    "vlan_id": "771"
}
calico_nodes =[
    {
        "hostname": "nkt-master-1",
        "ip": "192.168.20.1/24",
        "ipv6": "",
        "natip": "10.48.170.130",
        "rack_id": "1"
    },
    {
        "hostname": "nkt-master-2",
        "ip": "192.168.20.2/24",
        "ipv6": "",
        "natip": "10.48.170.131",
        "rack_id": "1"
    },
    {
        "hostname": "nkt-master-3",
        "ip": "192.168.20.3/24",
        "ipv6": "",
        "natip": "10.48.170.132",
        "rack_id": "1"
    }
]
vc ={
    "url": "10.48.170.23",
    "username": "administrator@dom.local",
    "pass": "C!sc0123",
    "dc": "DC1",
    "datastore": "Disk3-240M4",
    "cluster": "Compute",
    "dvs": "vc02-DC1",
    "port_group": "vlan_k8s1",
    "vm_template": "nkt_template",
    "vm_folder": "CiscoLive",
    "vm_deploy": true
}
k8s_cluster ={
    "control_plane_vip": "192.168.20.252",
    "vip_port": "8443",
    "pod_subnet": "192.168.21.0/24",
    "pod_subnet_v6": "",
    "cluster_svc_subnet": "192.168.22.0/24",
    "cluster_svc_subnet_v6": "",
    "external_svc_subnet": "192.168.23.0/24",
    "external_svc_subnet_v6": "",
    "local_as": "64635",
    "ingress_ip": "192.168.23.1",
    "visibility_ip": "192.168.23.2",
    "neo4j_ip": "192.168.23.3",
    "kubeadm_token": "fqv728.htdmfzf6rt9blhej",
    "node_sub": "192.168.20.0/24",
    "node_sub_v6": "",
    "ntp_server": "clock.cisco.com",
    "kube_version": "1.23.4-00",
    "crio_version": "1.23",
    "OS_Version": "xUbuntu_20.04",
    "haproxy_image": "haproxy:latest",
    "keepalived_image": "osixia/keepalived:latest",
    "keepalived_router_id": "51",
    "time_zone": "Europe/Rome",
    "docker_mirror": "10.67.185.120:5000",
    "http_proxy_status": "on",
    "http_proxy": "proxy.esl.cisco.com:8080",
    "ubuntu_apt_mirror": "",
    "sandbox_status": true,
    "eBPF_status": false,
    "dns_domain": "k8s.cisco.com",
    "dns_servers": [
        "10.48.170.50"
    ]
}