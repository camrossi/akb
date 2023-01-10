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

resource "aci_l3out_bgp_protocol_profile" "bgp_pol_timers" { 
  logical_node_profile_dn  = aci_logical_node_profile.calico_node_profile.id
  relation_bgp_rs_bgp_node_ctx_pol = aci_bgp_timers.bgp_timers.id
}


## Create BGP Address Family Context Policy
## Use to increase the Max eBGP and iBGP ECMP from 16 to 64 (current Maximum of ACI) the iBGP is used for the internal MP-BGP redistributed routes. 

resource "aci_bgp_address_family_context" "bgp_addr_family_context" {
  tenant_dn     = data.aci_tenant.tenant_l3out.id
  name          = var.l3out.name
  max_ecmp      = "64"
  max_ecmp_ibgp = "64"
}

resource "aci_vrf_to_bgp_address_family_context" "bgp_addr_family_context_to_vrf" {
  vrf_dn  = data.aci_vrf.l3out_vrf.id
  bgp_address_family_context_dn = aci_bgp_address_family_context.bgp_addr_family_context.id
  address_family  = "ipv4-ucast"
}

# Map BGP Address Family Context Policy to Calico VRF for V6
resource "aci_vrf_to_bgp_address_family_context" "bgp_addr_family_context_to_vrf_v6" {
  count = var.l3out.ipv6_enabled ? 1 : 0
  vrf_dn  = data.aci_vrf.l3out_vrf.id
  bgp_address_family_context_dn = aci_bgp_address_family_context.bgp_addr_family_context.id
  address_family  = "ipv6-ucast"
}
# Configure default-export policy to advertise the POD subnets back to the nodes

## Create Match Rule

resource "aci_match_rule" "export_match_rule" {
  tenant_dn       = data.aci_tenant.tenant_l3out.id
  name = "${var.l3out.name}-export-match"
}

## Create Match Rule Subnet

resource "aci_match_route_destination_rule" "export_pod_match_rule_subnet" {
  match_rule_dn       = aci_match_rule.export_match_rule.id
  ip = var.k8s_cluster.pod_subnet
  aggregate = "yes"
}

resource "aci_match_route_destination_rule" "export_pod_match_rule_subnet_v6" {
  count = var.l3out.ipv6_enabled ? 1 : 0
  match_rule_dn       = aci_match_rule.export_match_rule.id
  ip = var.k8s_cluster.pod_subnet_v6
  aggregate = "yes"
}

## Attach Rule to default-export policy

resource "aci_route_control_profile" "export_pod_subnet" {
  parent_dn                  = aci_l3_outside.calico_l3out.id
  name                       = "default-export"
}

## Create permit rule

resource "aci_route_control_context" "default_export" {
  route_control_profile_dn   = aci_route_control_profile.export_pod_subnet.id
  name                       = "export_pod_subnet"
  action                     = "permit"
  relation_rtctrl_rs_ctx_p_to_subj_p = [aci_match_rule.export_match_rule.id]
}

# Configure default-import policy to accept the POD, Node and SVCs subnets from the nodes

## Create Match Rule


resource "aci_match_rule" "import_match_rule" {
  tenant_dn       = data.aci_tenant.tenant_l3out.id
  name = "${var.l3out.name}-import-match"
}

## Create Match Rule Subnets

resource "aci_match_route_destination_rule" "import_pod_match_rule_subnet" {
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.k8s_cluster.pod_subnet
  aggregate = "yes"
}

resource "aci_match_route_destination_rule" "import_pod_match_rule_subnet_v6" {
  count = var.l3out.ipv6_enabled ? 1 : 0
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.k8s_cluster.pod_subnet_v6
  aggregate = "yes"

}

resource "aci_match_route_destination_rule" "import_node_match_rule_subnet" {
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.l3out.ipv4_cluster_subnet
  aggregate = "yes"
}

resource "aci_match_route_destination_rule" "import_node_match_rule_subnet_v6" {
  count = var.l3out.ipv6_enabled ? 1 : 0
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.k8s_cluster.node_sub_v6
  aggregate = "yes"
}

resource "aci_match_route_destination_rule" "import_svc_match_rule_subnet" {
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.k8s_cluster.cluster_svc_subnet
  aggregate = "yes"
}

resource "aci_match_route_destination_rule" "import_svc_match_rule_subnet_v6" {
  count = var.l3out.ipv6_enabled ? 1 : 0
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.k8s_cluster.cluster_svc_subnet_v6
  aggregate = "yes"
}

resource "aci_match_route_destination_rule" "import_ext_svc_match_rule_subnet" {
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.k8s_cluster.external_svc_subnet
  aggregate = "yes"
}

resource "aci_match_route_destination_rule" "import_ext_svc_match_rule_subnet_v6" {
  count = var.l3out.ipv6_enabled ? 1 : 0
  match_rule_dn       = aci_match_rule.import_match_rule.id
  ip = var.k8s_cluster.external_svc_subnet_v6
  aggregate = "yes"
}

## Attach Rule to default-export policy

resource "aci_route_control_profile" "default_import" {
  parent_dn                  = aci_l3_outside.calico_l3out.id
  name                       = "default-import"
}

## Create permit rule
resource "aci_route_control_context" "import_cluster_subnets" {
  route_control_profile_dn                  = aci_route_control_profile.default_import.id
  name                       = "import_cluster_subnets"
  action                     = "permit"
  relation_rtctrl_rs_ctx_p_to_subj_p = [aci_match_rule.import_match_rule.id]
}

resource "aci_bgp_peer_prefix" "bgp_peer_prefix" {
  tenant_dn    = data.aci_tenant.tenant_l3out.id
  name         = var.l3out.name
  action       = "reject"
  max_pfx      = "500"
}