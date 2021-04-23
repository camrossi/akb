# Configure Floating SVI for every Anchor Node
resource "aci_rest" "floating_svi" {
    depends_on = [ aci_logical_interface_profile.calico_interface_profile ]
    path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}.json"
    for_each = {for v in var.l3out.anchor_nodes:  v.node_id => v}
    class_name = "l3extVirtualLIfP"
      content = {
        "addr" = each.value.primary_ip
        "encap" = "vlan-${var.l3out.vlan_id}"
        "encapScope" = "local"
        "ifInstT" = "ext-svi"
        "mtu"     = var.l3out.mtu
        "nodeDn" = "topology/pod-${each.value.pod_id}/node-${each.value.node_id}"
  }
}

resource "aci_rest" "floating_svi_path" {
    depends_on = [ aci_rest.floating_svi ]
    path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]/rsdynPathAtt-[uni/phys-${var.l3out.physical_dom}].json"
    for_each = {for v in var.l3out.anchor_nodes:  v.node_id => v}
    class_name = "l3extRsDynPathAtt"
      content = {
        "floatingAddr" = var.l3out.floating_ip
        "tDn" = "uni/phys-${var.l3out.physical_dom}"
  }
}

resource "aci_rest" "floating_svi_sec_ip" {
    depends_on = [ aci_rest.floating_svi ]
    path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]/addr-[${var.l3out.secondary_ip}].json"
    for_each = {for v in var.l3out.anchor_nodes:  v.node_id => v}
    class_name = "l3extIp"
      content = {
        "addr" = var.l3out.secondary_ip
  }
}

#Add eBPG Peers

# Generate a  list of all the anchor-nodes and calico nodes for BPG peering only for the nodes in the same rack (see the if)
# I basically create the cartesian product (setproduct) of all the anchor_nodes and calico_nodes
# and then I build a  list of all the items to be user after by for_each
locals {
  peering = [for k, v in setproduct(var.l3out.anchor_nodes, var.calico_nodes): 
            {
                    node_id = v[0].node_id
                    pod_id = v[0].pod_id
                    calico_ip = split("/",v[1].ip)[0]
                    calico_as = v[1].local_as
                    index_key = join("_",[v[0].node_id, split("/",v[1].ip)[0]])
            } if v[0].rack_id == v[1].rack_id 
  ]

}

#output "name" {
#    value = local.peering
#}
# Create the BGP Peer
resource "aci_rest" "bgp_peer" {
  depends_on = [ aci_rest.floating_svi ]
  for_each = {for v in local.peering:  v.index_key => v}
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]/peerP-[${each.value.calico_ip}].json"
  class_name = "bgpPeerP"
      content = {
        "addr" = each.value.calico_ip
        "password" = var.l3out.bgp_pass

  }
}
# Set the Peer AS
resource "aci_rest" "bgp_peer_remote_as" {
  depends_on = [ aci_rest.bgp_peer ]
  for_each = {for v in local.peering:  v.index_key => v}
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}]/peerP-[${each.value.calico_ip}]/as.json"
  class_name = "bgpAsP"
      content = {
        "asn" = each.value.calico_as

  }
}

