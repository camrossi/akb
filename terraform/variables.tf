variable "apic_username" {
  type = string
}

variable "cert_name" {
  type = string
}

variable "private_key" {
  type = string
}

variable "apic_url" {
  type = string
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
  })
}


variable "dns_domain" {
  type = string
}

variable "dns_servers" {
  type = list(string)
}

variable "l3out" {
  type = object({
    name              = string
    l3out_tenant      = string
    vrf_tenant        = string
    vrf_name          = string
    node_profile_name = string
    int_prof_name     = string
    physical_dom      = string
    floating_ip       = string
    secondary_ip      = string
    vlan_id           = number
    def_ext_epg       = string
    def_ext_epg_scope = list(string)
    local_as          = number
    anchor_nodes      = list(object({
      node_id         = number
      rtr_id          = string
      rtr_id_loop_back= bool
      pod_id          = number
      primary_ip      = string
    }))
  })
}

variable "calico_nodes" {
  type = list(object({
    hostname        = string
    ip              = string
    local_as        = number
     }))
}

variable "k8s_cluster" {
  type = object({
    kube_version        = string
    crio_version        = string
    OS_Version          = string
    control_plane_vip   = string
    vip_port            = number
    haproxy_image       = string
    keepalived_image    = string
    keepalived_router_id= string
    kubeadm_token       = string
    node_sub            = string
    pod_subnet          = string
    cluster_svc_subnet  = string
    ntp_server          = string
    time_zone           = string
    docker_mirror       = string
     })
}