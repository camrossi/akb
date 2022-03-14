apic ={
    "username": "nkt_user_jnmdxa",
    "cert_name": "nkt_user_jnmdxa",
    "private_key": "../ansible/roles/aci/files/nkt_user_jnmdxa-user.key",
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
    "floating_ip": "192.168.0.254/24",
    "secondary_ip": "192.168.0.253/24",
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
    "anchor_nodes": [
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "101",
            "rtr_id": "1.1.1.1",
            "primary_ip": "192.168.0.101/24",
            "primary_ipv6": ""
        },
        {
            "pod_id": "1",
            "rack_id": "1",
            "node_id": "102",
            "rtr_id": "1.1.1.2",
            "primary_ip": "192.168.0.102/24",
            "primary_ipv6": ""
        }
    ],
    "ipv4_cluster_subnet": "192.168.0.0/24",
    "ipv6_cluster_subnet": "",
    "ipv6_enabled": false,
    "vlan_id": "666"
}
calico_nodes = null
vc ={
    "url": "",
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
    "pod_subnet": "192.168.1.0/24",
    "pod_subnet_v6": "",
    "cluster_svc_subnet": "192.168.2.0/24",
    "cluster_svc_subnet_v6": "",
    "external_svc_subnet": "192.168.3.0/24",
    "external_svc_subnet_v6": "",
    "local_as": "65002",
    "ingress_ip": "192.168.3.1",
    "visibility_ip": "192.168.3.2",
    "neo4j_ip": "192.168.3.3",
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
    "sandbox_status": false,
    "eBPF_status": false,
    "dns_domain": "",
    "dns_servers": [
        ""
    ]
}