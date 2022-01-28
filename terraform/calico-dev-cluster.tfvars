apic ={
    "url": "https://fab1-apic1.cam.ciscolabs.com",
    "username": "ansible",
    "cert_name": "ansible.crt",
    "private_key": "/home/cisco/Coding/ansible.key",
    "oob_ips": "10.67.185.106"
}
vc ={
    "url": "vc1.cam.ciscolabs.com",
    "username": "administrator@vsphere.local",
    "pass": "123Cisco123!",
    "dc": "STLD",
    "datastore": "ESXi3_SSD",
    "cluster": "Cluster1",
    "dvs": "ACI",
    "port_group": "calico_dev",
    "vm_template": "Ubuntu21-Template",
    "vm_folder": "Calico-Dev"
}
l3out ={
    "name": "calico_l3out",
    "l3out_tenant": "calico_dev",
    "vrf_tenant": "calico_dev",
    "vrf_name": "vrf",
    "node_profile_name": "node_profile_FL3out",
    "int_prof_name": "int_profile_FL3out",
    "int_prof_name_v6": "int_profile_v6_FL3out",
    "physical_dom": "FAB1",
    "floating_ipv6": "2001:db8:35:ff:ffff:ffff:ffff:fffe/56",
    "secondary_ipv6": "2001:db8:35:ff:ffff:ffff:ffff:fffd/56",
    "floating_ip": "192.168.35.254/24",
    "secondary_ip": "192.168.35.253/24",
    "def_ext_epg": "catch_all",
    "def_ext_epg_scope": [
        "import-security",
        "shared-rtctrl",
        "shared-security"
    ],
    "local_as": "65001",
    "mtu": "9000",
    "bgp_pass": "123Cisco123",
    "max_node_prefixes": "500",
    "contract": "calico_dev",
    "contract_tenant": "common",
    "dns_servers": [
        "10.67.185.100"
    ],
    "dns_domain": "cam.ciscolabs.com",
    "anchor_nodes": [
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "101",
            "rtr_id": "1.1.1.101",
            "primary_ip": "192.168.35.201/24",
            "primary_ipv6": "2001:db8:35::201/56"
        },
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "102",
            "rtr_id": "1.1.1.102",
            "primary_ip": "192.168.35.202/24",
            "primary_ipv6": "2001:db8:35::202/56"
        }
    ],
    "ipv4_cluster_subnet": "192.168.35.0/24",
    "ipv6_cluster_subnet": "2001:db8:35::/56",
    "vlan_id": "11"
}
calico_nodes =[
    {
        "hostname": "calico-1",
        "ip": "192.168.35.11/24",
        "ipv6": "2001:db8:35::11/56",
        "natip": "",
        "local_as": "650011",
        "rack_id": "1"
    },
    {
        "hostname": "calico-2",
        "ip": "192.168.35.12/24",
        "ipv6": "2001:db8:35::12/56",
        "natip": "",
        "local_as": "650011",
        "rack_id": "1"
    },
    {
        "hostname": "calico-3",
        "ip": "192.168.35.13/24",
        "ipv6": "2001:db8:35::13/56",
        "natip": "",
        "local_as": "650011",
        "rack_id": "1"
    },
    {
        "hostname": "calico-4",
        "ip": "192.168.35.14/24",
        "ipv6": "2001:db8:35::14/56",
        "natip": "",
        "local_as": "650011",
        "rack_id": "1"
    }
]
k8s_cluster ={
    "control_plane_vip": "192.168.35.2",
    "vip_port": "8443",
    "pod_subnet": "192.168.36.0/24",
    "pod_subnet_v6": "2001:db8:35:100::/56",
    "cluster_svc_subnet": "192.168.37.0/24",
    "cluster_svc_subnet_v6": "2001:db8:35:200::/108",
    "external_svc_subnet": "192.168.38.0/24",
    "external_svc_subnet_v6": "2001:db8:35:200::10:0/108",
    "ingress_ip": "192.168.38.1",
    "kubeadm_token": "fqv728.htdmfzf6rt9blhej",
    "node_sub": "192.168.35.0/24",
    "node_sub_v6": "2001:db8:35::/56",
    "ntp_server": "72.163.32.44",
    "kube_version": "1.22.4-00",
    "crio_version": "1.22",
    "OS_Version": "xUbuntu_21.04",
    "haproxy_image": "haproxy:latest",
    "keepalived_image": "osixia/keepalived:latest",
    "keepalived_router_id": "51",
    "time_zone": "Australia/Sydney",
    "docker_mirror": "10.67.185.120:5000",
    "http_proxy_status": "",
    "http_proxy": "",
    "ubuntu_apt_mirror": "ubuntu.mirror.digitalpacific.com.au/archive/"
}