# Enabled BPG

resource "aci_l3out_bgp_external_policy" "bgp" {

  l3_outside_dn  = aci_l3_outside.calico_l3out.id
}

# Create BGP Protocol Profile 

resource "aci_l3out_bgp_protocol_profile" "bgp_prot_pfl" {

  logical_node_profile_dn  = aci_logical_node_profile.calico_node_profile.id
}

## Configure BGP timers 1s Keepalive Interval and a 3s Hold Interval to align with the default configuration of Calico 
## Also enabled Graceful Restart and set the AS Limit to 2

resource "aci_bgp_timers" "bgp_timers" {
  tenant_dn    = data.aci_tenant.tenant_l3out.id
  name         = "${var.l3out.name}-Timers"
  gr_ctrl      = "helper"
  hold_intvl   = "3"
  ka_intvl     = "1"
  max_as_limit = "1"
  stale_intvl  = "6"
}

## Map Timers to BGP Protocol Profile 
## There is a bug on ACI that will have the destroy fail you can do this 
## terraform state rm  aci_rest.bgp_pol_timers
resource "aci_rest" "bgp_pol_timers" {
  depends_on = [ aci_l3out_bgp_protocol_profile.bgp_prot_pfl ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/protp/rsbgpNodeCtxPol.json"
  class_name = "bgpRsBgpNodeCtxPol"
    content = {
      "tnBgpCtxPolName" = "${var.l3out.name}-Timers"
  }
}

#not working https://github.com/CiscoDevNet/terraform-provider-aci/issues/415
#resource "aci_l3out_bgp_protocol_profile" "bgp_pol_timers" { 
#
#  logical_node_profile_dn  = aci_logical_node_profile.calico_node_profile.id
#  relation_bgp_rs_bgp_node_ctx_pol = aci_bgp_timers.bgp_timers.id
#}

## Set BGP Route Control Enforcement to Import/Export 

resource "aci_rest" "bgp_route_control" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}.json"
  class_name = "l3extOut"
    content = {
      "enforceRtctrl" = "export,import"
  }
}


## Create BGP Best Path Policy

resource "aci_bgp_best_path_policy" "relax_as_policy" {
    tenant_dn  = data.aci_tenant.tenant_l3out.id
    name  = "${var.l3out.name}-Relax-AS"
    ctrl = "asPathMultipathRelax"
}

## Map BGP Best Path Policy to BGP Protocol Profile 
resource "aci_rest" "bgp_pol_relax_as_restriction" {
  depends_on = [ aci_l3out_bgp_protocol_profile.bgp_prot_pfl ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/lnodep-${var.l3out.node_profile_name}/protp/rsBestPathCtrlPol.json"
  class_name = "bgpRsBestPathCtrlPol"
    content = {
      "tnBgpBestPathCtrlPolName" = "${var.l3out.name}-Relax-AS"
  }
}

## Create BGP Address Family Context Policy
## Use to increase the Max eBGP and iBGP ECMP from 16 to 64 (current Maximum of ACI) the iBGP is used for the internal MP-BGP redistributed routes. 

resource "aci_bgp_address_family_context" "bgp_addr_family_context" {
  tenant_dn     = data.aci_tenant.tenant_l3out.id
  name          = var.l3out.name
  max_ecmp      = "64"
  max_ecmp_ibgp = "64"
}

# Map BGP Address Family Context Policy to Calico VRF
resource "aci_rest" "bgp_addr_family_context_to_vrf" {
  depends_on = [ aci_bgp_address_family_context.bgp_addr_family_context ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/ctx-${var.l3out.vrf_name}/rsctxToBgpCtxAfPol-[${var.l3out.name}]-ipv4-ucast.json"
  class_name = "fvRsCtxToBgpCtxAfPol"
    content = {
      "tnBgpCtxAfPolName" = var.l3out.name
      "af" = "ipv4-ucast"
  }
}

# Configure default-export policy to advertise the POD subnets back to the nodes

## Create Match Rule

resource "aci_rest" "export_match_rule" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-export-match.json"
  class_name = "rtctrlSubjP"
    content = {
      "name" = "${var.l3out.name}-export-match"
  }
}

## Create Match Rule Subnet

resource "aci_rest" "export_pod_match_rule_subnet" {
  depends_on = [ aci_rest.export_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-export-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.pod_subnet
      "aggregate" = "yes"
  }
}

resource "aci_rest" "export_pod_match_rule_subnet_v6" {
  depends_on = [ aci_rest.export_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-export-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.pod_subnet_v6
      "aggregate" = "yes"
  }
}

## Attach Rule to default-export policy

resource "aci_bgp_route_control_profile" "export_pod_subnet" {
  parent_dn                  = aci_l3_outside.calico_l3out.id
  name                       = "default-export"
}

## Create permit rule

resource "aci_rest" "default_export" {
  depends_on = [ aci_bgp_route_control_profile.export_pod_subnet ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/prof-default-export.json"
  class_name = "rtctrlCtxP"
    content = {
      "action" = "permit"
      "name"   = "export_pod_subnet"
      "order"  = "0"
  }
}

## Add Match Rule to Permit Rule
resource "aci_rest" "default_export_match_rule" {
  depends_on = [ aci_rest.default_export ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/prof-default-export/ctx-export_pod_subnet.json"
  class_name = "rtctrlRsCtxPToSubjP"
    content = {
      "tnRtctrlSubjPName" = "${var.l3out.name}-export-match"
  }
}

# Configure default-import policy to accept the POD, Node and SVCs subnets from the nodes

## Create Match Rule


resource "aci_rest" "import_match_rule" {
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlSubjP"
    content = {
      "name" = "${var.l3out.name}-import-match"
  }
}

## Create Match Rule Subnets

resource "aci_rest" "import_pod_match_rule_subnet" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.pod_subnet
      "aggregate" = "yes"
  }
}

resource "aci_rest" "import_pod_match_rule_subnet_v6" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.pod_subnet_v6
      "aggregate" = "yes"
  }
}

resource "aci_rest" "import_node_match_rule_subnet" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.node_sub
      "aggregate" = "yes"
  }
}

resource "aci_rest" "import_node_match_rule_subnet_v6" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.node_sub_v6
      "aggregate" = "yes"
  }
}

resource "aci_rest" "import_svc_match_rule_subnet" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.cluster_svc_subnet
      "aggregate" = "yes"
  }
}

resource "aci_rest" "import_svc_match_rule_subnet_v6" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.cluster_svc_subnet_v6
      "aggregate" = "yes"
  }
}

resource "aci_rest" "import_ext_svc_match_rule_subnet" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.external_svc_subnet
      "aggregate" = "yes"
  }
}

resource "aci_rest" "import_ext_svc_match_rule_subnet_v6" {
  depends_on = [ aci_rest.import_match_rule ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/subj-${var.l3out.name}-import-match.json"
  class_name = "rtctrlMatchRtDest"
    content = {
      "ip" = var.k8s_cluster.external_svc_subnet_v6
      "aggregate" = "yes"
  }
}

## Attach Rule to default-export policy

resource "aci_bgp_route_control_profile" "default_import" {
  parent_dn                  = aci_l3_outside.calico_l3out.id
  name                       = "default-import"
}

## Create permit rule

resource "aci_rest" "import_cluster_subnets" {
  depends_on = [ aci_bgp_route_control_profile.default_import ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/prof-default-import.json"
  class_name = "rtctrlCtxP"
    content = {
      "action" = "permit"
      "name"   = "import_cluster_subnets"
      "order"  = "0"
  }
}

## Add Match Rule to Permit Rule
resource "aci_rest" "default_import_match_rule" {
  depends_on = [ aci_rest.import_cluster_subnets ]
  path       = "/api/mo/uni/tn-${var.l3out.l3out_tenant}/out-${var.l3out.name}/prof-default-import/ctx-import_cluster_subnets.json"
  class_name = "rtctrlRsCtxPToSubjP"
    content = {
      "tnRtctrlSubjPName" = "${var.l3out.name}-import-match"
  }
}

resource "aci_bgp_peer_prefix" "bgp_peer_prefix" {
  tenant_dn    = data.aci_tenant.tenant_l3out.id
  name         = var.l3out.name
  action       = "reject"
  max_pfx      = "500"
}