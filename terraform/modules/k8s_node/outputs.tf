### Generate Ansible inventory file
resource "local_file" "AnsibleInventory" {
  content = templatefile("${path.module}/inventory.tmpl",
    {
      k8s_primary_master  = var.calico_nodes[0]
      k8s_master_replicas = slice(var.calico_nodes, 1, 3)
      k8s_workers         = slice(var.calico_nodes, 3, length(var.calico_nodes))
      http_proxy_status   = var.k8s_cluster.http_proxy_status
    }
  )
  filename = "${var.ansible_dir}/inventory/nodes.ini"
}
### Generate Ansible config file
resource "local_file" "AnsibleConfig" {
  content = templatefile("${path.module}/group_var_template.tmpl",
    {
      k8s_cluster     = var.k8s_cluster
      vc              = var.vc
      calico_nodes    = var.calico_nodes
      as              = var.fabric.as
      bgp_pass        = var.fabric.bgp_pass
      bgp_peers       = var.bgp_peers
      dns_domain      = var.k8s_cluster.dns_domain
      vrf_tenant      = var.fabric.vrf_tenant
      vrf_name        = var.fabric.vrf_name
      controller      = var.controller
      fabric_type     = var.fabric.type
      ssh_private_key = abspath("${var.ansible_dir}/roles/sandbox/files/id_rsa")
    }
  )
  filename = "${var.ansible_dir}/inventory/group_vars/all.yml"
}

# Run ansible-playbook to provision the baremetal cluster
resource "null_resource" "AnsibleInventory" {
  count      = var.k8s_cluster.sandbox_status ? 0 : 1
  depends_on = [local_file.AnsibleInventory, local_file.AnsibleConfig]
  triggers = {
    ansible_dir = "${var.ansible_dir}"
  }
  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -i ${self.triggers.ansible_dir}/inventory/nodes.ini ${self.triggers.ansible_dir}/cluster.yaml"
  }
}