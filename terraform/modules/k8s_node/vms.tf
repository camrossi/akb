provider "vsphere" {
  user           = var.vc.username
  password       = var.vc.pass
  vsphere_server = var.vc.url
  # If you have a self-signed cert
  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name = var.vc.dc
}

data "vsphere_datastore" "datastore" {
  name          = var.vc.datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = var.vc.cluster
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "template" {
  name          = var.vc.vm_template
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_distributed_virtual_switch" "dvs" {
  name          = var.vc.dvs
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name                            = var.vc.port_group
  datacenter_id                   = data.vsphere_datacenter.dc.id
  distributed_virtual_switch_uuid = data.vsphere_distributed_virtual_switch.dvs.id
}

resource "tls_private_key" "ansible_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "vsphere_virtual_machine" "vm" {
  for_each = { for v in var.calico_nodes : v.hostname => v }
    lifecycle {
    ignore_changes = [vapp, ]
  }
  name                        = each.value.hostname
  resource_pool_id            = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id                = data.vsphere_datastore.datastore.id
  num_cpus                    = 2
  memory                      = 8192
  guest_id                    = data.vsphere_virtual_machine.template.guest_id
  scsi_type                   = data.vsphere_virtual_machine.template.scsi_type
  folder                      = var.vc.vm_folder
  wait_for_guest_net_routable = true
  wait_for_guest_net_timeout = 10

  network_interface {
    network_id   = data.vsphere_network.network.id
    adapter_type = data.vsphere_virtual_machine.template.network_interface_types[0]
  }

  cdrom {
    client_device = true
  }

  disk {
    label            = "disk0"
    size             = data.vsphere_virtual_machine.template.disks.0.size
    eagerly_scrub    = data.vsphere_virtual_machine.template.disks.0.eagerly_scrub
    thin_provisioned = data.vsphere_virtual_machine.template.disks.0.thin_provisioned
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.template.id
    linked_clone  = "true"

    customize {
      linux_options {
        host_name = each.value.hostname
        domain    = var.k8s_cluster.dns_domain
      }

      network_interface {
        ipv4_address = split("/", each.value.ip)[0]
        ipv4_netmask = split("/", each.value.ip)[1]
        ipv6_address = var.fabric.ipv6_enabled ? split("/", each.value.ipv6)[0] : null
        ipv6_netmask = var.fabric.ipv6_enabled ? split("/", each.value.ipv6)[1] : null
      }
      dns_server_list = var.k8s_cluster.dns_servers
      ipv4_gateway    = split("/", var.fabric.ip)[0]
      ipv6_gateway    = var.fabric.ipv6_enabled ? split("/", var.fabric.ipv6)[0] : null

    }
  }
    #vapp {
    #properties = {
    #  instance-id = each.value.hostname
    #  public-keys = tls_private_key.ansible_key.public_key_openssh
    #  password = "123Cisco123"
    #}
  #}
}


resource "null_resource" "cluster" {
  count      = var.k8s_cluster.sandbox_status ? 0 : 1
  depends_on = [local_file.AnsibleInventory, local_file.AnsibleConfig, vsphere_virtual_machine.vm]
  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -i ${var.ansible_dir}/inventory/nodes.ini ${var.ansible_dir}/cluster.yml"
  }

}

resource "null_resource" "sandbox_cluster" {
  count      = var.k8s_cluster.sandbox_status ? 1 : 0
  depends_on = [local_file.AnsibleInventory, local_file.AnsibleConfig, vsphere_virtual_machine.vm]
  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -i ${var.ansible_dir}/inventory/nodes.ini ${var.ansible_dir}/sandbox_cluster.yml"
  }
}
