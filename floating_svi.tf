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