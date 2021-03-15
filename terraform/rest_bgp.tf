# Enabled BPG
resource "aci_rest" "bgp" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/bgpExtP.json"
  depends_on = [ aci_l3_outside.calico_l3out ]
  payload = <<EOF
                    {
                        "bgpExtP": {
                            "attributes": {
                                "dn": "uni/tn-common/out-calico_l3out/bgpExtP",
                                "userdom": ":all:common:"
                            }
                        }
                    }
EOF
}

# Create Relax AS-Path restriction Policy

resource "aci_rest" "as_restriction" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}.json"
  payload = <<EOF
        {
            "bgpBestPathCtrlPol": {
                "attributes": {
                    "annotation": "",
                    "ctrl": "asPathMultipathRelax",
                    "descr": "",
                    "dn": "uni/tn-common/bestpath-${var.l3out.name}-Relax-AS",
                    "name": "${var.l3out.name}-Relax-AS",
                    "nameAlias": "",
                    "userdom": ":all:common:"
                }
            }
        }
EOF
}

# Map AS-Path restriction Policy to L3OUT

resource "aci_rest" "as_restriction_l3out" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}.json"
  depends_on = [ aci_logical_node_profile.calico_node_profile ]
  payload = <<EOF

        {
            "bgpProtP": {
                "attributes": {
                    "userdom": ":all:common:"
                },
                "children": [
                    {
                        "bgpRsBestPathCtrlPol": {
                            "attributes": {
                                "tnBgpBestPathCtrlPolName": "${var.l3out.name}-Relax-AS",
                                "userdom": ":all:common:"
                            }
                        }
                    }
                ]
            }
        }
EOF
}