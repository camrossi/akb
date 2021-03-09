provider "vsphere" {
  user           = var.vsphere_user
  password       = var.vsphere_password
  vsphere_server = var.vsphere_server

  # If you have a self-signed cert
  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name = "STLD"
}

data "vsphere_datastore" "datastore" {
  name          = "BM01"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = "Cluster"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "template" {
  name          = "Ubuntu20-Template"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_distributed_virtual_switch" "dvs" {
  name          = "ACI"
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name          = "CalicoL3OUT_300"
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
        dns_server_list = var.dns_servers
      }

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
