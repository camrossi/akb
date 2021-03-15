
terraform {
 required_providers {
   aci = {
     source = "CiscoDevNet/aci"
     version = "0.5.4"
   }
   vsphere = {
      source = "hashicorp/vsphere"
      version = "1.24.3"
    }
 }
}

provider "aci" {
  # cisco-aci user name
  username = var.apic_username
  cert_name = var.cert_name
  private_key = var.private_key
  # cisco-aci password
  #password = var.apic_password
  # cisco-aci url
  url      = var.apic_url 
  insecure = true
}

data "aci_tenant" "tenant_l3out" {
  name  = var.l3out.l3out_tenant
}

data "aci_vrf" "l3out_vrf" {
  tenant_dn  = data.aci_tenant.tenant_l3out.id
  name       = var.l3out.vrf_name
}

resource "aci_l3_outside" "calico_l3out" {
  tenant_dn      = data.aci_tenant.tenant_l3out.id
  name           = var.l3out.name
  relation_l3ext_rs_ectx = data.aci_vrf.l3out_vrf.id
}

resource "aci_logical_node_profile" "calico_node_profile" {
  l3_outside_dn = aci_l3_outside.calico_l3out.id
  name          = var.l3out.node_profile_name
}


resource "aci_logical_node_to_fabric_node" "nodes" {
  logical_node_profile_dn = aci_logical_node_profile.calico_node_profile.id
  for_each = {for i, v in var.l3out.anchor_nodes:  i => v}
    tdn = "topology/pod-${each.value.pod_id}/node-${each.value.node_id}"
    rtr_id = each.value.rtr_id
}

resource "aci_logical_interface_profile" "calico_interface_profile" {
    logical_node_profile_dn = aci_logical_node_profile.calico_node_profile.id
    name                    = var.l3out.int_prof_name
  }    

data "aci_contract" "default" {
  tenant_dn  = data.aci_tenant.tenant_l3out.id
  name       = "default"
} 

resource "aci_external_network_instance_profile" "default" {
        l3_outside_dn  = aci_l3_outside.calico_l3out.id
        name           = var.l3out.def_ext_epg
        relation_fv_rs_prov = [ data.aci_contract.default.id] 
        relation_fv_rs_cons = [data.aci_contract.default.id]

    }

resource "aci_l3_ext_subnet" "node" {
  external_network_instance_profile_dn  = aci_external_network_instance_profile.default.id
  ip                                    = var.l3out.calico_node_sub
  scope                                 = var.l3out.def_ext_epg_scope
}

resource "aci_l3_ext_subnet" "pod" {
  external_network_instance_profile_dn  = aci_external_network_instance_profile.default.id
  ip                                    = var.l3out.calico_pod_sub
  scope                                 = var.l3out.def_ext_epg_scope
  aggregate                             = "shared-rtctrl"
}

resource "aci_l3_ext_subnet" "cluster_svc" {
  external_network_instance_profile_dn  = aci_external_network_instance_profile.default.id
  ip                                    = var.l3out.calico_svc_sub
  scope                                 = var.l3out.def_ext_epg_scope
  aggregate                             = "shared-rtctrl"
}