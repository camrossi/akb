provider "vsphere" {
  user           = var.vc.username
  password       = var.vc.pass
  vsphere_server = var.vc.url
  # If you have a self-signed cert
  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name = "STLD"
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
  name          = var.vc.port_group
  datacenter_id = data.vsphere_datacenter.dc.id
  distributed_virtual_switch_uuid = data.vsphere_distributed_virtual_switch.dvs.id
}

resource "vsphere_virtual_machine" "vm" {
  for_each = {for v in var.calico_nodes:  v.hostname => v}
  name             = each.value.hostname
  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id
  num_cpus = 2
  memory   = 8192
  guest_id = data.vsphere_virtual_machine.template.guest_id
  scsi_type = data.vsphere_virtual_machine.template.scsi_type
  folder = var.vc.vm_folder
  network_interface {
    network_id   = data.vsphere_network.network.id
    adapter_type = data.vsphere_virtual_machine.template.network_interface_types[0]
  }

  disk {
    label            = "disk0"
    size             = data.vsphere_virtual_machine.template.disks.0.size
    eagerly_scrub    = data.vsphere_virtual_machine.template.disks.0.eagerly_scrub
    thin_provisioned = data.vsphere_virtual_machine.template.disks.0.thin_provisioned
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.template.id
    linked_clone = "true"

    customize {
      linux_options {
        host_name = each.value.hostname
        domain    = var.dns_domain
      }

      network_interface {
        ipv4_address = split("/",each.value.ip)[0]
        ipv4_netmask = split("/",each.value.ip)[1]
      }
      dns_server_list = var.dns_servers
      ipv4_gateway = split("/",var.l3out.secondary_ip)[0]
    }
  }
}

resource "null_resource" "build_inventory" {
  for_each = {for v in var.calico_nodes:  v.hostname => v}
  triggers = {
    always_run = timestamp()
  }

    provisioner "local-exec" {
        command = <<EOF
        echo "[${each.value.hostname}]\n "${split("/",each.value.ip)[0]}" " | tee -a nodes.ini;
        EOF
    }
}
