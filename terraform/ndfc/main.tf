module "k8s_node" {
  source       = "../modules/k8s_node"
  fabric_type  = var.fabric_type
  vc           = var.vc
  calico_nodes = var.calico_nodes
  k8s_cluster  = var.k8s_cluster
  bgp_peers    = var.bgp_peers
}

module "overlay" {
  source      = "../modules/overlay"
  overlay     = var.overlay
  ndfc        = var.ndfc
  k8s_cluster = var.k8s_cluster
}
