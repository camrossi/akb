### Generate Ansible config file
resource "local_file" "AnsibleConfig" {
  content = templatefile("group_var_template_novm.tmpl",
    {
      k8s_cluster  = var.k8s_cluster
      as           = var.l3out.local_as
      bgp_pass     = var.l3out.bgp_pass
      anchor_nodes = var.l3out.anchor_nodes
      dns_domain   = var.l3out.dns_domain
      vrf_tenant   = var.l3out.vrf_tenant
      vrf_name     = var.l3out.vrf_name
      apic         = var.apic
    }
  )
  filename = "../ansible/inventory/group_vars/all.yml"
}


