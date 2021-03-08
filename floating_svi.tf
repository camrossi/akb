# Enabled BPG
resource "aci_rest" "bgp" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}.json"
  depends_on = [ aci_l3_outside.calico_l3out ]
  payload = <<EOF
                    {
                        "bgpExtP": {
                            "attributes": {
                                "annotation": "",
                                "descr": "",
                                "nameAlias": "",
                                "userdom": ":all:common:"
                            }
                        }
                    }
EOF
}

# Configure Floating SVI for every Anchor Node
resource "aci_rest" "floating_svi" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}.json"
  depends_on = [ aci_logical_interface_profile.calico_interface_profile ]
  for_each = {for i, v in var.l3out.anchor_nodes:  i => v}
  payload = <<EOF
  {
            "l3extVirtualLIfP": {
                "attributes": {
                    "addr": "${each.value.primary_ip}",
                    "encap": "vlan-${var.l3out.vlan_id}",
                    "encapScope": "local",
                    "ifInstT": "ext-svi",
                    "nodeDn": "topology/pod-${each.value.pod_id}/node-${each.value.node_id}",
                },
                "children": [
                    {
                        "l3extRsDynPathAtt": {
                            "attributes": {
                                "annotation": "",
                                "floatingAddr": "${var.l3out.floating_ip}",
                                "forgedTransmit": "Disabled",
                                "macChange": "Disabled",
                                "promMode": "Disabled",
                                "tDn": "uni/phys-${var.l3out.physical_dom}",
                                "userdom": ":all:common:"
                            }
                        }
                    },
                    {
                        "l3extIp": {
                            "attributes": {
                                "addr": "${var.l3out.secondary_ip}",
                                "userdom": ":all:common:"
                            }
                        }
                    }
                ]
            }
        }
  EOF
}

#Add eBPG Peers

# Generate a  list of all the anchor-nodes and calico nodes for BPG peering 
# I basically create the cartesian product (setproduct) of all the anchor_nodes and calico_nodes
# and then I build a  list of all the items to be user after by for_each
locals {
  peering = [for k, v in setproduct(var.l3out.anchor_nodes, var.calico_nodes): {
                    node_id = v[0].node_id
                    pod_id = v[0].pod_id
                    calico_ip = split("/",v[1].ip)[0]
                    calico_as = v[1].local_as
                    }
  ]

}

#output "name" {
#    value = local.peering
#}

resource "aci_rest" "bgp_peer" {
  for_each = {for i, v in local.peering:  i => v}
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/lifp-${var.l3out.int_prof_name}/vlifp-[topology/pod-${each.value.pod_id}/node-${each.value.node_id}]-[vlan-${var.l3out.vlan_id}].json"
  depends_on = [ aci_rest.floating_svi ]
  payload = <<EOF
{
            "bgpPeerP": {
                "attributes": {
                    "addr": "${each.value.calico_ip}",
                    "addrTCtrl": "af-ucast",
                    "adminSt": "enabled",
                    "allowedSelfAsCnt": "3",
                    "annotation": "",
                    "ctrl": "",
                    "descr": "",
                    "name": "",
                    "nameAlias": "",
                    "peerCtrl": "",
                    "privateASctrl": "",
                    "ttl": "1",
                    "userdom": ":all:common:",
                    "weight": "0"
                },
                "children": [
                    {
                        "bgpRsPeerPfxPol": {
                            "attributes": {
                                "annotation": "",
                                "tnBgpPeerPfxPolName": "",
                                "userdom": "all"
                            }
                        }
                    },
                    {
                        "bgpLocalAsnP": {
                            "attributes": {
                                "annotation": "",
                                "asnPropagate": "none",
                                "descr": "",
                                "localAsn": "${var.l3out.local_as}",
                                "name": "",
                                "nameAlias": "",
                                "userdom": ":all:common:"
                            }
                        }
                    },
                    {
                        "bgpAsP": {
                            "attributes": {
                                "annotation": "",
                                "asn": "${each.value.calico_as}",
                                "descr": "",
                                "name": "",
                                "nameAlias": "",
                                "userdom": ":all:common:"
                            }
                        }
                    }
                ]
            }
        }
        EOF
}