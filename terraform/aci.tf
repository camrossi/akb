

terraform {
  required_providers {
    aci = {
      source  = "CiscoDevNet/aci"
      version = "2.4.0"
      #source = "terraform.local/CiscoDevNet/aci"
      #version = "2.3.0"
    }
    vsphere = {
      source  = "hashicorp/vsphere"
      version = "2.0.2"
    }
  }
}
module "k8s_node" {
  source       = "./modules/k8s_node"
  
  vc           = var.vc
  calico_nodes = var.calico_nodes
  k8s_cluster  = var.k8s_cluster
  bgp_peers    = var.l3out.anchor_nodes
  controller   = {
    username = var.apic.nkt_user
    url = var.apic.url
    cert_name = var.apic.cert_name
    private_key = var.apic.private_key
    oob_ips = var.apic.oob_ips
    password = ""
  }
  fabric  = {
    type  = "aci"
    ip = var.l3out.secondary_ip
    ipv6 = var.l3out.secondary_ipv6
    ipv6_enabled = var.l3out.ipv6_enabled
    as =  var.l3out.local_as
    bgp_pass = var.l3out.bgp_pass
    vrf_tenant = var.l3out.vrf_tenant
    vrf_name   =  var.l3out.vrf_name
  }
 ansible_dir = "../ansible"
}

provider "aci" {
  # cisco-aci user name
  username    = var.apic.nkt_user
  cert_name   = var.apic.cert_name
  private_key = var.apic.private_key
  url         = var.apic.url
  insecure    = true
}

data "aci_tenant" "tenant_l3out" {
  name = var.l3out.l3out_tenant
}

data "aci_tenant" "tenant_contract" {
  name = var.l3out.contract_tenant
}

data "aci_vrf" "l3out_vrf" {
  tenant_dn = data.aci_tenant.tenant_l3out.id
  name      = var.l3out.vrf_name
}



resource "aci_l3_outside" "calico_l3out" {
  tenant_dn              = data.aci_tenant.tenant_l3out.id
  name                   = var.l3out.name
  relation_l3ext_rs_ectx = data.aci_vrf.l3out_vrf.id
  enforce_rtctrl         = ["export", "import"]
}

resource "aci_logical_node_profile" "calico_node_profile" {
  l3_outside_dn = aci_l3_outside.calico_l3out.id
  name          = var.l3out.node_profile_name
}


resource "aci_logical_node_to_fabric_node" "nodes" {
  logical_node_profile_dn = aci_logical_node_profile.calico_node_profile.id
  for_each                = { for i, v in var.l3out.anchor_nodes : i => v }
  tdn                     = "topology/pod-${each.value.pod_id}/node-${each.value.node_id}"
  rtr_id                  = each.value.rtr_id
  rtr_id_loop_back        = "no"
}

resource "aci_logical_interface_profile" "calico_interface_profile" {
  logical_node_profile_dn = aci_logical_node_profile.calico_node_profile.id
  name                    = var.l3out.int_prof_name
}

resource "aci_logical_interface_profile" "calico_interface_profile_v6" {
  count                   = var.l3out.ipv6_enabled ? 1 : 0
  logical_node_profile_dn = aci_logical_node_profile.calico_node_profile.id
  name                    = var.l3out.int_prof_name_v6
}

data "aci_contract" "default" {
  tenant_dn = data.aci_tenant.tenant_contract.id
  name      = var.l3out.contract
}

resource "aci_external_network_instance_profile" "default" {
  l3_outside_dn       = aci_l3_outside.calico_l3out.id
  name                = var.l3out.def_ext_epg
  relation_fv_rs_prov = [data.aci_contract.default.id]
  relation_fv_rs_cons = [data.aci_contract.default.id]

}

resource "aci_l3_ext_subnet" "node" {
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.l3out.ipv4_cluster_subnet
  scope                                = var.l3out.def_ext_epg_scope
}

resource "aci_l3_ext_subnet" "pod" {
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.k8s_cluster.pod_subnet
  scope                                = var.l3out.def_ext_epg_scope
  aggregate                            = "shared-rtctrl"
}

resource "aci_l3_ext_subnet" "cluster_svc" {
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.k8s_cluster.cluster_svc_subnet
  scope                                = var.l3out.def_ext_epg_scope
  aggregate                            = "shared-rtctrl"
}

resource "aci_l3_ext_subnet" "external_svc_subnet" {
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.k8s_cluster.external_svc_subnet
  scope                                = var.l3out.def_ext_epg_scope
  aggregate                            = "shared-rtctrl"
}

resource "aci_l3_ext_subnet" "node_v6" {
  count                                = var.l3out.ipv6_enabled ? 1 : 0
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.k8s_cluster.node_sub_v6
  scope                                = var.l3out.def_ext_epg_scope
}

resource "aci_l3_ext_subnet" "pod_v6" {
  count                                = var.l3out.ipv6_enabled ? 1 : 0
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.k8s_cluster.pod_subnet_v6
  scope                                = var.l3out.def_ext_epg_scope
  aggregate                            = "shared-rtctrl"
}

resource "aci_l3_ext_subnet" "cluster_svc_v6" {
  count                                = var.l3out.ipv6_enabled ? 1 : 0
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.k8s_cluster.cluster_svc_subnet_v6
  scope                                = var.l3out.def_ext_epg_scope
  aggregate                            = "shared-rtctrl"
}

resource "aci_l3_ext_subnet" "external_svc_subnet_v6" {
  count                                = var.l3out.ipv6_enabled ? 1 : 0
  external_network_instance_profile_dn = aci_external_network_instance_profile.default.id
  ip                                   = var.k8s_cluster.external_svc_subnet_v6
  scope                                = var.l3out.def_ext_epg_scope
  aggregate                            = "shared-rtctrl"
}
