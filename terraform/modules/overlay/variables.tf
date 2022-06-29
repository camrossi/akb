variable "ndfc" {
  type = object({
    username = string
    password = string
    url      = string
    platform = string
  })
}

variable "overlay" {
  type = object({
    fabric_name    = string
    vrf            = string
    asn            = string
    bgp_passwd     = string
    ibgp_peer_vlan = number
    k8s_route_map  = string
    route_tag      = number
    gateway_v4     = string
    gateway_v6     = string
    ipv6_enabled   = bool
    k8s_integ      = bool
    vpc_peers = list(
      list(object({
        hostname       = string
        loopback_id    = number
        loopback_ipv4  = string
        loopback_ipv6  = string
        ibgp_svi_ipv4  = string
        ibgp_peer_ipv4 = string
        ibgp_svi_ipv6  = string
        ibgp_peer_ipv6 = string
        })
    ))
  })
}

variable "k8s_cluster" {
  type = object({
    kube_version           = string
    crio_version           = string
    OS_Version             = string
    control_plane_vip      = string
    vip_port               = number
    local_as               = number
    peer_as                = number
    bgp_passwd             = string
    haproxy_image          = string
    keepalived_image       = string
    keepalived_router_id   = string
    kubeadm_token          = string
    node_sub               = string
    node_sub_v6            = string
    pod_subnet             = string
    pod_subnet_v6          = string
    cluster_svc_subnet     = string
    cluster_svc_subnet_v6  = string
    external_svc_subnet    = string
    external_svc_subnet_v6 = string
    ingress_ip             = string
    ntp_servers            = list(string)
    dns_servers            = list(string)
    dns_domain             = string
    time_zone              = string
    docker_mirror          = string
    http_proxy_status      = string
    http_proxy             = string
    ubuntu_apt_mirror      = string
    sandbox_status         = bool
  })
}
