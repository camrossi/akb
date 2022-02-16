apic ={
    "username": "akb_user_lbuzdb",
    "cert_name": "akb_user_lbuzdb",
    "private_key": "../ansible/roles/aci/files/akb_user_lbuzdb-user.key",
    "url": "https://fab1-apic1.cam.ciscolabs.com",
    "oob_ips": "10.67.185.106"
}
vc ={
    "url": "vc1.cam.ciscolabs.com",
    "username": "administrator@vsphere.local",
    "pass": "123Cisco123!",
    "dc": "STLD",
    "datastore": "ESXi1_SSD",
    "cluster": "Cluster1",
    "dvs": "ACI",
    "port_group": "calico_dev_v4",
    "vm_template": "Ubuntu21SandBox",
    "vm_folder": "CalicoDev_v4"
}
l3out ={
    "name": "CalicoL3OUT",
    "l3out_tenant": "calico_dev_v4",
    "vrf_tenant": "calico_dev_v4",
    "vrf_name": "vrf",
    "node_profile_name": "node_profile_FL3out",
    "int_prof_name": "int_profile_FL3out",
    "int_prof_name_v6": "int_profile_v6_FL3out",
    "physical_dom": "FAB1",
    "floating_ipv6": "",
    "secondary_ipv6": "",
    "floating_ip": "192.168.39.254/24",
    "secondary_ip": "192.168.39.253/24",
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
    "contract": "calico_dev_ssh_only",
    "contract_tenant": "common",
    "dns_servers": [
        "10.67.185.100"
    ],
    "dns_domain": "cisco.com",
    "anchor_nodes": [
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "101",
            "rtr_id": "1.1.1.1",
            "primary_ip": "192.168.39.101/24",
            "primary_ipv6": ""
        },
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "102",
            "rtr_id": "1.1.1.2",
            "primary_ip": "192.168.39.102/24",
            "primary_ipv6": ""
        }
    ],
    "ipv4_cluster_subnet": "192.168.39.0/24",
    "ipv6_cluster_subnet": "",
    "ipv6_enabled": false,
    "vlan_id": "11"
}
calico_nodes =[
    {
        "hostname": "akb-master-1",
        "ip": "192.168.39.1/24",
        "ipv6": "",
        "natip": "",
        "rack_id": "1"
    },
    {
        "hostname": "akb-master-2",
        "ip": "192.168.39.2/24",
        "ipv6": "",
        "natip": "",
        "rack_id": "1"
    },
    {
        "hostname": "akb-master-3",
        "ip": "192.168.39.3/24",
        "ipv6": "",
        "natip": "",
        "rack_id": "1"
    }
]
k8s_cluster ={
    "control_plane_vip": "192.168.39.252",
    "vip_port": "8443",
    "pod_subnet": "192.168.40.0/24",
    "pod_subnet_v6": "",
    "cluster_svc_subnet": "192.168.41.0/24",
    "cluster_svc_subnet_v6": "",
    "external_svc_subnet": "192.168.42.0/24",
    "external_svc_subnet_v6": "",
    "local_as": "65002",
    "ingress_ip": "192.168.42.1",
    "kubeadm_token": "fqv728.htdmfzf6rt9blhej",
    "node_sub": "192.168.39.0/24",
    "node_sub_v6": "",
    "ntp_server": "",
    "kube_version": "1.23.3-00",
    "crio_version": "1.23",
    "OS_Version": "xUbuntu_21.04",
    "haproxy_image": "haproxy:latest",
    "keepalived_image": "osixia/keepalived:latest",
    "keepalived_router_id": "51",
    "time_zone": "Australia/Sydney",
    "docker_mirror": "",
    "http_proxy_status": "",
    "http_proxy": "",
    "ubuntu_apt_mirror": "",
    "sandbox_status": true
}