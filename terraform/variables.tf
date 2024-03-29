variable "apic" {
  type = object({
  nkt_user          = string
  cert_name         = string
  private_key       = string
  url               = string
  oob_ips           = string
  })
}

variable "calico_nodes" {
  type = list(object({
    hostname        = string
    ip              = string
    ipv6            = string
    natip           = string
    rack_id         = string
     }))
}

variable "vc" {
  type = object({
  url               = string
  username          = string
  pass              = string
  dc                = string
  datastore         = string
  cluster           = string
  dvs               = string
  port_group        = string
  vm_template       = string
  vm_folder         = string
  vm_deploy         = bool
  bare_metal        = bool
  })
}

variable "k8s_cluster" {
  type = object({
    kube_version        = string
    crio_version        = string
    OS_Version          = string
    control_plane_vip   = string
    vip_port            = number
    local_as            = number
    keepalived_router_id= string
    kubeadm_token       = string
    node_sub            = string
    node_sub_v6         = string
    pod_subnet          = string
    pod_subnet_v6       = string
    cluster_svc_subnet  = string
    cluster_svc_subnet_v6  = string
    external_svc_subnet = string
    external_svc_subnet_v6 = string
    ingress_ip          = string
    neo4j_ip            = string
    visibility_ip       = string
    ntp_servers         = list(string)
    time_zone           = string
    docker_mirror       = string
    http_proxy_status   = string
    http_proxy          = string
    ubuntu_apt_mirror   = string
    sandbox_status      = bool
    eBPF_status         = bool
    dns_servers       = list(string)
    dns_domain        = string
    cni_plugin        = string
    ansible_user      = string
     })
}

variable "l3out" {
  type = object({
    ipv6_enabled      = bool
    name              = string
    l3out_tenant      = string
    vrf_tenant        = string
    vrf_name          = string
    node_profile_name = string
    int_prof_name     = string
    int_prof_name_v6  = string
    physical_dom      = string
    floating_ipv6     = string
    secondary_ipv6    = string
    floating_ip       = string
    secondary_ip      = string
    vlan_id           = number
    def_ext_epg       = string
    def_ext_epg_scope = list(string)
    local_as          = number
    mtu               = number
    bgp_pass          = string
    max_node_prefixes = number
    contract          = string
    contract_tenant   = string
    ipv4_cluster_subnet = string
    ipv6_cluster_subnet = string
    anchor_nodes      = list(object({
      node_id         = number
      rtr_id          = string
      pod_id          = number
      ip              = string
      ipv6            = string
      rack_id         = string
    }))
  })
}

variable "fabric_type" {
  type    = string
  default = "aci"
}