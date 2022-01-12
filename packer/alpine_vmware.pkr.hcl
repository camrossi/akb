packer {
  required_plugins {
    vmware = {
      version = ">= 1.0.3"
      source = "github.com/hashicorp/vmware"
    }
  }
}
# Need to install:
##apk add open-vm-tools
##apk add open-vm-tools-guestinfo
##apk add open-vm-tools-deploypkg
##rc-update add open-vm-tools default


# "timestamp" template function replacement
locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

# source blocks are analogous to the "builders" in json templates. They are used
# in build blocks. A build block runs provisioners and post-processors on a
# source. Read the documentation for source blocks here:
# https://www.packer.io/docs/templates/hcl_templates/blocks/source
source "vsphere-clone" "clone" {
  template            = "alpine3.15"
  boot_wait            = "10s"
  cluster = "Cluster"
  host = "esxi4.cam.ciscolabs.com"
  datastore = "esxi4-SSD2"
  insecure_connection  = true
  username       = "administrator@vsphere.local"
  password     = "123Cisco123!"
  vcenter_server = "vc2.cam.ciscolabs.com"
  vm_name        = "alpine-${local.timestamp}"
  ssh_username = "root"
  ssh_password = "123Cisco123"
}

# a build block invokes sources and runs provisioning steps on them. The
# documentation for build blocks can be found here:
# https://www.packer.io/docs/templates/hcl_templates/blocks/build
build {
  sources = ["source.vsphere-clone.clone"]

  provisioner "shell" {
    inline = [
      "apk update",
      "apk upgrade",
      "apk add python3 py3-pip gcc",
      "wget https://aci-github.cisco.com/camrossi/calico_aci/archive/master.zip",
      "unzip master.zip",
      "pip3 install -r calico_aci-master/requirements.txt",

    ]
  }
}