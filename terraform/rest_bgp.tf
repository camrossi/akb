# Enabled BPG

resource "aci_rest" "bgp" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/bgpExtP.json"
  depends_on = [ aci_l3_outside.calico_l3out ]
  class_name = "bgpExtP"
      content = {
      "userdom" = ":all:common:"
    }
}

# Create BGP Protocol Profile 

resource "aci_rest" "bgp_prot_pfl" {
  depends_on = [ aci_logical_node_profile.calico_node_profile ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}.json"
  class_name = "bgpProtP"
    content = {
      "userdom" = ":all:common:"
  }
}

## Configure BGP timers 1s Keepalive Interval and a 3s Hold Interval to align with the default configuration of Calico 
## Also enabled Graceful Restart and set the AS Limit to 2
resource "aci_rest" "bgp_timers" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}.json"
  class_name = "bgpCtxPol"
      content = {
          "holdIntvl"  = "3"
          "kaIntvl"    =  "1"
          "maxAsLimit" = "2"
          "name"       = "${var.l3out.name}-Timers"
          "staleIntvl" = "6"
          "grCtrl"     = "helper"
        }
}

## Create BGP Best Path Policy

resource "aci_rest" "relax_as_policy" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/bestpath-${var.l3out.name}-Relax-AS.json"
  class_name = "bgpBestPathCtrlPol"
    content = {
      "ctrl" = "asPathMultipathRelax"
  }
}

## Map BGP Best Path Policy to BGP Protocol Profile 
resource "aci_rest" "bgp_pol_relax_as_restriction" {
  depends_on = [ aci_rest.bgp_prot_pfl ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/protp/rsBestPathCtrlPol.json"
  class_name = "bgpRsBestPathCtrlPol"
    content = {
      "tnBgpBestPathCtrlPolName" = "${var.l3out.name}-Relax-AS"
  }
}

## Map Timers to BGP Protocol Profile 
resource "aci_rest" "bgp_pol_timers" {
  depends_on = [ aci_rest.bgp_prot_pfl ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/protp/rsbgpNodeCtxPol.json"
  class_name = "bgpRsBgpNodeCtxPol"
    content = {
      "tnBgpCtxPolName" = "${var.l3out.name}-Timers"
  }
}



# Configure default-export policy to advertise the POD subnets back to the nodes

## Create Match Rule

resource "aci_rest" "match_rule" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-Match.json"
  class_name = "rtctrlSubjP"
    content = {
      "name" = "${var.l3out.name}-Match"
  }
}

## Create Match Rule Subnet

resource "aci_rest" "match_rule_subnet" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-Match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.pod_subnet
      "aggregate" = "yes"
  }
}

## Attach Rule to default-export policy

resource "aci_rest" "export_pod_subnet" {
  depends_on = [ aci_l3_outside.calico_l3out ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/prof-default-export.json"
  class_name = "rtctrlProfile"
    content = {
      "name" = "default-export"
  }
}

## Create permit rule

resource "aci_rest" "default_export" {
  depends_on = [ aci_rest.export_pod_subnet ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/prof-default-export.json"
  class_name = "rtctrlCtxP"
    content = {
      "action" = "permit"
      "name"   = "export_pod_subnet"
      "order"  = "0"
  }
}

## Add Match Rule to Permit Rule
resource "aci_rest" "default_export_match_rule1" {
  depends_on = [ aci_rest.default_export ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/prof-default-export/ctx-export_pod_subnet.json"
  class_name = "rtctrlRsCtxPToSubjP"
    content = {
      "tnRtctrlSubjPName" = "${var.l3out.name}-Match"
  }
}