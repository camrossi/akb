variable "controller" {
  type = object({
    username    = string
    password    = string
    cert_name   = string
    private_key = string
    url         = string
    oob_ips     = string
  })
  default = {
    username    = ""
    url         = ""
    password    = ""
    cert_name   = ""
    private_key = ""
    oob_ips     = ""
  }
}

variable "fabric" {
  type = object({
    type         = string
    ip           = string
    ipv6         = string
    ipv6_enabled = bool
    as           = number
    bgp_pass     = string
    vrf_tenant   = string
    vrf_name     = string
  })
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
    hostname = string
    ip       = string
    ipv6     = string
    natip    = string
    rack_id  = string
  }))
}

variable "bgp_peers" {
  type = list(object({
    node_id = number
    ip      = string
    ipv6    = string
    rack_id = number
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
    neo4j_ip               = string
    visibility_ip          = string
    ntp_server             = string
    dns_servers            = list(string)
    dns_domain             = string
    time_zone              = string
    docker_mirror          = string
    http_proxy_status      = string
    http_proxy             = string
    ubuntu_apt_mirror      = string
    sandbox_status         = bool
    eBPF_status            = bool
    dns_servers            = list(string)
    dns_domain             = string
    cni_plugin             = string
  })
}
variable "ansible_dir" {
  type = string
}
