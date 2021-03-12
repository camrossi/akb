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

variable "vsphere_user" {
  type = string
}

variable "vsphere_password" {
  type = string

}

variable "vsphere_server" {
  type = string 
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
    calico_node_sub   = string
    calico_svc_sub   = string
    calico_pod_sub   = string
    local_as          = number
    anchor_nodes      = list(object({
      node_id         = number
      rtr_id          = string
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

