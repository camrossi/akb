terraform {
  required_providers {
    dcnm = {
      source  = "CiscoDevNet/dcnm"
      version = "1.1.0"
    }
  }
}

provider "dcnm" {
  username = var.ndfc.username
  password = var.ndfc.password
  url      = var.ndfc.url
  platform = var.ndfc.platform
}


locals {
  switches = flatten([
    for peers in var.overlay.vpc_peers : [
      for peer in peers : {
        switch_name    = peer.hostname
        loopback_id    = peer.loopback_id
        loopback_ipv4  = peer.loopback_ipv4
        loopback_ipv6  = peer.loopback_ipv6
        ibgp_svi_ipv4  = peer.ibgp_svi_ipv4
        ibgp_peer_ipv4 = peer.ibgp_peer_ipv4
        ibgp_svi_ipv6  = peer.ibgp_svi_ipv6
        ibgp_peer_ipv6 = peer.ibgp_peer_ipv6
      }
    ]
  ])
}

data "dcnm_inventory" "vpc_peer" {
  for_each = {
    for switch in local.switches : "${switch.switch_name}" => switch
  }
  fabric_name = var.overlay.fabric_name
  switch_name = each.value.switch_name
}

resource "dcnm_interface" "loopbacks" {
  for_each = {
    for switch in local.switches : "${switch.switch_name}" => switch
  }
  fabric_name   = var.overlay.fabric_name
  type          = "loopback"
  name          = "loopback${each.value.loopback_id}"
  policy        = "int_loopback"
  switch_name_1 = each.value.switch_name
  vrf           = var.overlay.vrf
  ipv4          = each.value.loopback_ipv4
  ipv6          = each.value.loopback_ipv6
  loopback_tag  = var.overlay.route_tag
  deploy        = true
}

resource "dcnm_policy" "infra_vlan" {
  for_each      = data.dcnm_inventory.vpc_peer
  serial_number = each.value.serial_number
  description   = "k8s ibgp peer vlan of ${var.k8s_cluster.node_sub}"
  priority      = 450
  template_name = "system_nve_infra_vlan"
  template_props = {
    "VLAN" = var.overlay.ibgp_peer_vlan
  }
}

resource "dcnm_policy" "k8s_route_map" {
  for_each = {
    for switch in local.switches : "${switch.switch_name}" => switch
  }
  serial_number = data.dcnm_inventory.vpc_peer[each.value.switch_name].serial_number
  description   = "k8s route map node peering ${var.k8s_cluster.node_sub} "
  entity_name   = "SWITCH"
  entity_type   = "SWITCH"
  priority      = 430
  template_name = "switch_freeform"
  template_props = {
    "CONF" = templatefile(
      "${path.module}/route_map_k8s.tmpl", {
        "k8s_route_map" = var.overlay.k8s_route_map
        "route_tag"     = var.overlay.route_tag
    })
  }
}

resource "dcnm_policy" "vrf_ibgp_peer" {
  for_each = {
    for switch in local.switches : "${switch.switch_name}" => switch
  }
  serial_number = data.dcnm_inventory.vpc_peer[each.value.switch_name].serial_number
  description   = "k8s ibgp peer of ${var.k8s_cluster.node_sub}"
  entity_name   = "SWITCH"
  entity_type   = "SWITCH"
  priority      = 430
  template_name = "switch_freeform"
  template_props = {
    "CONF" = templatefile(
      "${path.module}/vpc_ibgp_peer.tmpl", {
        "vrf"               = var.overlay.vrf
        "asn"               = var.overlay.asn
        "bgp_passwd"        = var.overlay.bgp_passwd
        "k8s_route_map"     = var.overlay.k8s_route_map
        "route_tag"         = var.overlay.route_tag
        "k8s_cluster_asn"   = var.k8s_cluster.local_as
        "k8s_node_subnetv4" = var.k8s_cluster.node_sub
        "k8s_node_subnetv6" = var.k8s_cluster.node_sub_v6
        "loopback_id"       = each.value.loopback_id
        "loopback_ipv4"     = each.value.loopback_ipv4
        "loopback_ipv6"     = each.value.loopback_ipv6
        "ibgp_peer_vlan"    = var.overlay.ibgp_peer_vlan
        "ibgp_svi_ipv4"     = each.value.ibgp_svi_ipv4
        "ibgp_peer_ipv4"    = each.value.ibgp_peer_ipv4
        "ibgp_svi_ipv6"     = each.value.ibgp_svi_ipv6
        "ibgp_peer_ipv6"    = each.value.ibgp_peer_ipv6
    })
  }
}
