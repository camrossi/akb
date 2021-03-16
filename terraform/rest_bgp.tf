# Enabled BPG

resource "aci_rest" "bgp" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/bgpExtP.json"
  depends_on = [ aci_l3_outside.calico_l3out ]
  class_name = "bgpExtP"
      content = {
      "userdom" = ":all:common:"
    }
}

# Create Relax AS-Path restriction Policy

resource "aci_rest" "bgp_prot_pfl" {
  depends_on = [ aci_logical_node_profile.calico_node_profile ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}.json"
  class_name = "bgpProtP"
    content = {
      "userdom" = ":all:common:"
  }
}

resource "aci_rest" "bgp_relax_as_restriction" {
  depends_on = [ aci_rest.bgp_prot_pfl ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/protp/rsBestPathCtrlPol.json"
  class_name = "bgpRsBestPathCtrlPol"
    content = {
      "tnBgpBestPathCtrlPolName" = "${var.l3out.name}-Relax-AS"
  }
}

# Map AS-Path restriction Policy to L3OUT

resource "aci_rest" "relax_as_policy" {
  depends_on = [ aci_rest.bgp ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/bestpath-${var.l3out.name}-Relax-AS.json"
  class_name = "bgpBestPathCtrlPol"
    content = {
      "ctrl" = "asPathMultipathRelax"
  }
}


# Due to https://github.com/CiscoDevNet/terraform-provider-aci/issues/204 I can't use payload so need to create more objects 
#resource "aci_rest" "bgp" {
#  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/bgpExtP.json"
#  depends_on = [ aci_l3_outside.calico_l3out ]
#  payload = <<EOF
#                    {
#                        "bgpExtP": {
#                            "attributes": {
#                                "dn": "uni/tn-common/out-calico_l3out/bgpExtP",
#                                "userdom": ":all:common:"
#                            }
#                        }
#                    }
#EOF
#}

#resource "aci_rest" "as_restriction" {
#  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}.json"
#  payload = <<EOF
#        {
#            "bgpBestPathCtrlPol": {
#                "attributes": {
#                    "annotation": "",
#                    "ctrl": "asPathMultipathRelax",
#                    "descr": "",
#                    "dn": "uni/tn-common/bestpath-${var.l3out.name}-Relax-AS",
#                    "name": "${var.l3out.name}-Relax-AS",
#                    "nameAlias": "",
#                    "userdom": ":all:common:"
#                }
#            }
#        }
#EOF
#}


#resource "aci_rest" "as_restriction_l3out" {
#  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}.json"
#  payload = <<EOF
#
#        {
#            "bgpProtP": {
#                "attributes": {
#                    "userdom": ":all:common:"
#                },
#                "children": [
#                    {
#                        "bgpRsBestPathCtrlPol": {
#                            "attributes": {
#                                "tnBgpBestPathCtrlPolName": "${var.l3out.name}-Relax-AS",
#                                "userdom": ":all:common:"
#                            }
#                        }
#                    }
#                ]
#            }
#        }
#EOF
#}