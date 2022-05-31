# Configure Floating SVI for every Anchor Node
data "aci_physical_domain" "dom" {
  name = var.l3out.physical_dom
}
resource "aci_l3out_floating_svi" "floating_svi" {
  logical_interface_profile_dn = aci_logical_interface_profile.calico_interface_profile.id
  for_each                     = { for v in var.l3out.anchor_nodes : v.node_id => v }
  node_dn                      = "topology/pod-${each.value.pod_id}/node-${each.value.node_id}"
  encap                        = "vlan-${var.l3out.vlan_id}"
  addr                         = each.value.ip
  autostate                    = "enabled"
  encap_scope                  = "local"
  if_inst_t                    = "ext-svi"
  mtu                          = var.l3out.mtu
  relation_l3ext_rs_dyn_path_att {
    tdn              = data.aci_physical_domain.dom.id
    floating_address = var.l3out.floating_ip
    forged_transmit  = "Disabled"
    mac_change       = "Disabled"
    promiscuous_mode = "Disabled"
  }
}



resource "aci_l3out_path_attachment_secondary_ip" "floating_svi_sec_ip" {
  depends_on               = [aci_l3out_floating_svi.floating_svi]
  for_each                 = { for v in var.l3out.anchor_nodes : v.node_id => v }
  l3out_path_attachment_dn = "uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]"
  addr                     = var.l3out.secondary_ip
}

###### OLD WAY OF ADDING ONE PEER PER NODE WITH DIFFERENT NODE PER AS ######
#Add eBPG Peers

# Generate a  list of all the anchor-nodes and calico nodes for BPG peering only for the nodes in the same rack (see the if)
# I basically create the cartesian product (setproduct) of all the anchor_nodes and calico_nodes
# and then I build a  list of all the items to be user after by for_each
#locals {
#  peering = [for k, v in setproduct(var.l3out.anchor_nodes, var.calico_nodes): 
#            {
#                    node_id = v[0].node_id
#                    pod_id = v[0].pod_id
#                    calico_ip = split("/",v[1].ip)[0]
#                    k8s_cluster_as = v[1].local_as
#                    index_key = join("_",[v[0].node_id, split("/",v[1].ip)[0]])
#            } if v[0].rack_id == v[1].rack_id 
#  ]
#
#}
#
##output "name" {
##    value = local.peering
##}
## Create the BGP Peer
#resource "aci_rest" "bgp_peer" {
#  depends_on = [ aci_l3out_floating_svi.floating_svi ]
#  for_each = {for v in local.peering:  v.index_key => v}
#  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]/peerP-[${each.value.calico_ip}].json"
#  class_name = "bgpPeerP"
#      content = {
#        "addr" = each.value.calico_ip
#        "password" = var.l3out.bgp_pass
#
#  }
#}

#resource "aci_rest" "bgp_peer_remote_as" {
#  depends_on = [ aci_rest.bgp_peer ]
#  for_each = {for v in local.peering:  v.index_key => v}
#  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]/peerP-[${each.value.calico_ip}]/as.json"
#  class_name = "bgpAsP"
#      content = {
#        "asn" = each.value.k8s_cluster_as
#
#  }
#}
#
#
#resource "aci_rest" "bgp_peer_prefix" {
#  depends_on = [ aci_rest.bgp_peer ]
#  for_each = {for v in local.peering:  v.index_key => v}
#  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]/peerP-[${each.value.calico_ip}]/rspeerPfxPol.json"
#  class_name = "bgpRsPeerPfxPol"
#      content = {
#        "tnBgpPeerPfxPolName" = aci_bgp_peer_prefix.bgp_peer_prefix.name
#
#  }
#}

###### NEW WAY ALL NODE WITH THE SAME AS AND PEERING WITH THE SUBNET ######
resource "aci_bgp_peer_connectivity_profile" "bgp_peer" {
  for_each                     = aci_l3out_floating_svi.floating_svi
  parent_dn                    = each.value.id
  addr                         = var.l3out.ipv4_cluster_subnet
  ctrl                         = ["as-override", "dis-peer-as-check"]
  as_number                    = var.k8s_cluster.local_as
  relation_bgp_rs_peer_pfx_pol = aci_bgp_peer_prefix.bgp_peer_prefix.id
  password                     = var.l3out.bgp_pass
}

