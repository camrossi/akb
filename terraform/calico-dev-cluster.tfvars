apic ={
    "username": "nkt_user_aavlbc",
    "cert_name": "nkt_user_aavlbc",
    "private_key": "../ansible/roles/aci/files/nkt_user_aavlbc-user.key",
    "url": "https://fab1-apic1.cam.ciscolabs.com",
    "oob_ips": "10.67.185.106"
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
            "primary_ip": "192.168.39.101/24",
            "primary_ipv6": ""
        },
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "102",
            "rtr_id": "1.1.1.102",
            "primary_ip": "192.168.39.102/24",
            "primary_ipv6": ""
        }
    ],
    "ipv4_cluster_subnet": "192.168.39.0/24",
    "ipv6_cluster_subnet": "",
    "ipv6_enabled": false,
    "vlan_id": "11"
}
vc ={
    "url": "dummy",
    "username": "",
    "pass": "",
    "dc": "",
    "datastore": "",
    "cluster": "",
    "dvs": "",
    "port_group": "",
    "vm_template": "",
    "vm_folder": "",
    "vm_deploy": false
}
k8s_cluster ={
    "control_plane_vip": "",
    "vip_port": null,
    "pod_subnet": "192.168.40.0/24",
    "pod_subnet_v6": "",
    "cluster_svc_subnet": "192.168.41.0/24",
    "cluster_svc_subnet_v6": "",
    "external_svc_subnet": "192.168.42.0/24",
    "external_svc_subnet_v6": "",
    "local_as": "65002",
    "ingress_ip": "192.168.42.1",
    "visibility_ip": "192.168.42.2",
    "neo4j_ip": "192.168.42.3",
    "kubeadm_token": "",
    "node_sub": "",
    "node_sub_v6": "",
    "ntp_server": "",
    "kube_version": "",
    "crio_version": "",
    "OS_Version": "",
    "haproxy_image": "",
    "keepalived_image": "",
    "keepalived_router_id": "",
    "time_zone": "",
    "docker_mirror": "",
    "http_proxy_status": "",
    "http_proxy": "",
    "ubuntu_apt_mirror": "",
    "sandbox_status": true
}

calico_nodes = null