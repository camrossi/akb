variable "fabric_type" {
  type    = string
  default = "aci"
}

variable "vc" {
  type = object({
    url         = string
    username    = string
    pass        = string
    dc          = string
    datastore   = string
    cluster     = string
    dvs         = string
    port_group  = string
    vm_template = string
    vm_folder   = string
  })
}

variable "calico_nodes" {
  type = list(object({
    hostname     = string
    ip           = string
    ip_gateway   = string
    ipv6         = string
    ipv6_gateway = string
    natip        = string
    rack_id      = string
  }))
}

variable "bgp_peers" {
  type = list(object({
    node_id  = number
    ip       = string
    ipv6     = string
    rack_id  = number
    peer_asn = number
  }))
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
    ipv6_enabled           = bool
    node_sub               = string
    node_sub_v6            = string
    pod_subnet             = string
    pod_subnet_v6          = string
    cluster_svc_subnet     = string
    cluster_svc_subnet_v6  = string
    external_svc_subnet    = string
    external_svc_subnet_v6 = string
    ingress_ip             = string
    ntp_server             = string
    dns_servers            = list(string)
    dns_domain             = string
    time_zone              = string
    docker_mirror          = string
    http_proxy_status      = string
    http_proxy             = string
    ubuntu_apt_mirror      = string
    apt_upgrade            = bool
    sandbox_status         = bool
  })
}
variable "ansible_dir" {
  type    = string
  default = "../../ansible/"
}
