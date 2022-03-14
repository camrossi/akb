fabric_type = "vxlan_evpn"

vc = {
  "url" : "172.25.74.45",
  "username" : "admin",
  "pass" : "ins3965!",
  "dc" : "dc-cylon",
  "datastore" : "vsan_datastore",
  "cluster" : "cluster-cylon",
  "dvs" : "dvs-cylon",
  "port_group" : "k8s_node_vlan205",
  "vm_template" : "ubuntu-21.04-server-cloudimg-amd64",
  "vm_folder" : "akb_k8s_node"
}

ndfc = {
  "username" : "admin",
  "password" : "ins3965!",
  "url" : "https://172.25.74.47",
  "platform" : "nd"
}

overlay = {
  "fabric_name" : "fabric-cylon",
  "asn" : "65004"
  "vrf" : "k8s_cluster",
  "ibgp_peer_vlan" : 3965,
  "bgp_passwd" : "",
  "k8s_route_map" : "k8s_route_map_filter_out",
  "route_tag" : 65535,
  "vpc_peers" : [
      [
        {
          "hostname" : "93240YC-FX2-L02-S4",
          "loopback_id" : 100 
          "loopback_ipv4" : "10.100.100.10",
          "loopback_ipv6" : "",
          "ibgp_svi_ipv4" : "192.168.10.1/30"
          "ibgp_peer_ipv4" : "192.168.10.2",
          "ibgp_svi_ipv6" : "",
          "ibgp_peer_ipv6" : ""
        },
        {
          "hostname" : "93240YC-FX2-L01-S4",
          "loopback_id" : 100 
          "loopback_ipv4" : "10.100.100.20",
          "loopback_ipv6" : "",
          "ibgp_svi_ipv4" : "192.168.10.2/30"
          "ibgp_peer_ipv4" : "192.168.10.1",
          "ibgp_svi_ipv6" : "",
          "ibgp_peer_ipv6" : ""
        },
      ],
      [
        {
          "hostname" : "93180YC-FX-L04-S4",
          "loopback_id" : 100 
          "loopback_ipv4" : "10.100.100.10",
          "loopback_ipv6" : "",
          "ibgp_svi_ipv4" : "192.168.10.5/30"
          "ibgp_peer_ipv4" : "192.168.10.6",
          "ibgp_svi_ipv6" : "",
          "ibgp_peer_ipv6" : ""
        },
        {
          "hostname" : "93180YC-FX-L03-S4",
          "loopback_id" : 100 
          "loopback_ipv4" : "10.100.100.20",
          "loopback_ipv6" : "",
          "ibgp_svi_ipv4" : "192.168.10.6/30"
          "ibgp_peer_ipv4" : "192.168.10.5",
          "ibgp_svi_ipv6" : "",
          "ibgp_peer_ipv6" : ""
        },
      ],
  ]
}

bgp_peers = [
  {
    "node_id" : 1,
    "ip" : "10.100.100.10",
    "ipv6" : "",
    "peer_asn" : "65004",
    "rack_id" : 1
  },
  {
    "node_id" : 2,
    "ip" : "10.100.100.20",
    "ipv6" : "",
    "peer_asn" : "65004",
    "rack_id" : 1
  },
]

calico_nodes = [
  {
    "hostname" : "k8s-master-1",
    "ip" : "10.13.0.1/24",
    "ip_gateway" : "10.13.0.254"
    "ipv6" : "",
    "ipv6_gateway" : "2001:10:13::254"
    "natip" : "",
    "rack_id" : "1"
  },
  {
    "hostname" : "k8s-master-2",
    "ip" : "10.13.0.2/24",
    "ip_gateway" : "10.13.0.254"
    "ipv6" : "",
    "ipv6_gateway" : "2001:10:13::254"
    "natip" : "",
    "rack_id" : "1"
  },
  {
    "hostname" : "k8s-master-3",
    "ip" : "10.13.0.3/24",
    "ip_gateway" : "10.13.0.254"
    "ipv6" : "",
    "ipv6_gateway" : "2001:10:13::254"
    "natip" : "",
    "rack_id" : "1"
  },
  {
    "hostname" : "k8s-worker-1",
    "ip" : "10.13.0.4/24",
    "ip_gateway" : "10.13.0.254"
    "ipv6" : "",
    "ipv6_gateway" : "2001:10:13::254"
    "natip" : "",
    "rack_id" : "1"
  },
  {
    "hostname" : "k8s-worker-2",
    "ip" : "10.13.0.5/24",
    "ip_gateway" : "10.13.0.254"
    "ipv6" : "",
    "ipv6_gateway" : "2001:10:13::254"
    "natip" : "",
    "rack_id" : "1"
  },
  {
    "hostname" : "k8s-worker-3",
    "ip" : "10.13.0.6/24",
    "ip_gateway" : "10.13.0.254"
    "ipv6" : "",
    "ipv6_gateway" : "2001:10:13::254"
    "natip" : "",
    "rack_id" : "1"
  },
]

k8s_cluster = {
  "control_plane_vip" : "10.13.0.252",
  "vip_port" : "8443",
  "ipv6_enabled" : false,
  "pod_subnet" : "10.13.1.0/24",
  "pod_subnet_v6" : "",
  "cluster_svc_subnet" : "10.13.2.0/24",
  "cluster_svc_subnet_v6" : "",
  "external_svc_subnet" : "10.13.3.0/24",
  "external_svc_subnet_v6" : "",
  "local_as" : "65005",
  "peer_as" : "65004",
  "bgp_passwd" : ""
  "ingress_ip" : "10.13.3.1",
  "visibility_ip": "110.13.3.2",
  "neo4j_ip": "10.13.3.3",
  "kubeadm_token" : "fqv728.htdmfzf6rt9blhej",
  "node_sub" : "10.13.0.0/24",
  "node_sub_v6" : "2001:10:13::/64",
  "ntp_server" : "10.195.225.200",
  "dns_domain" : "cisco.com",
  "dns_servers" : ["10.195.200.67"],
  "kube_version" : "1.23.3-00",
  "crio_version" : "1.23",
  "OS_Version" : "xUbuntu_21.04",
  "haproxy_image" : "haproxy:latest",
  "keepalived_image" : "osixia/keepalived:latest",
  "keepalived_router_id" : "51",
  "time_zone" : "America/Los_Angeles",
  "docker_mirror" : "registry-shdu.cisco.com",
  "http_proxy_status" : "on",
  "http_proxy" : "proxy.esl.cisco.com:80",
  "ubuntu_apt_mirror" : "dal.mirrors.clouvider.net/ubuntu/",
  "sandbox_status" : false,
  "eBPF_status": false
} 