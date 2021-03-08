variable "apic_username" {
  type = string
}

variable "apic_password" {
  type = string
}

variable "apic_url" {
  type = string
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
    anchor_nodes      = list(object({
      node_id         = number
      rtr_id          = string
      pod_id          = number
      primary_ip      = string
    }))
  })
}

