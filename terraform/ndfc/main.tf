module "k8s_node" {
  source = "../modules/k8s_node"

  vc           = var.vc
  calico_nodes = var.calico_nodes
  k8s_cluster  = var.k8s_cluster
  bgp_peers    = var.bgp_peers
  controller = {
    username    = var.ndfc.username
    password    = var.ndfc.password
    url         = var.ndfc.url
    platform    = var.ndfc.platform
    cert_name   = ""
    private_key = ""
    oob_ips     = ""
  }
  fabric = {
    type         = var.fabric_type
    ip           = "${var.calico_nodes[0].ip_gateway}"
    ipv6         = "${var.calico_nodes[0].ipv6_gateway}"
    ipv6_enabled = var.k8s_cluster.ipv6_enabled
    as           = var.overlay.asn
    bgp_pass     = var.overlay.bgp_passwd
    vrf_tenant   = ""
    vrf_name     = var.overlay.vrf
  }
  ansible_dir = "../../ansible"

}

module "overlay" {
  source      = "../modules/overlay"
  overlay     = var.overlay
  ndfc        = var.ndfc
  k8s_cluster = var.k8s_cluster
}

resource "local_file" "ansible_ndfc_inventory" {
  content = templatefile("./ndfc.yaml.tmpl",
    {
      ndfc               = var.ndfc
      k8s_primary_master = var.calico_nodes[0]
      ndfc_k8s_user      = var.ndfc_k8s_user
      vcenter            = var.vc.url
    }
  )
  filename = "../../ansible/inventory/ndfc.yaml"
}

resource "null_resource" "cluster" {
  count      = var.ndfc_k8s_integ ? 1 : 0
  depends_on = [local_file.ansible_ndfc_inventory, module.k8s_node, module.overlay]
  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -i ${var.ansible_dir}/inventory/ndfc.yaml ${var.ansible_dir}/ndfc_integration.yaml --skip-tags reset"
  }
}
