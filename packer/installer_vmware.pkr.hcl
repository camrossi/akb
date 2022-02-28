packer {
  required_plugins {
    vmware = {
      version = ">= 1.0.3"
      source = "github.com/hashicorp/vmware"
    }
  }
}
# The tempalte Need to have:
##apt install open-vm-tools



# "timestamp" template function replacement
locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

# source blocks are analogous to the "builders" in json templates. They are used
# in build blocks. A build block runs provisioners and post-processors on a
# source. Read the documentation for source blocks here:
# https://www.packer.io/docs/templates/hcl_templates/blocks/source
source "vsphere-clone" "clone" {
  template            = "Ubutu21Desktop"
  linked_clone = true
  boot_wait            = "10s"
  datacenter = "STLD"
  cluster = "Cluster"
  host = "esxi3.cam.ciscolabs.com"
  datastore = "ESXi3_SSD"
  insecure_connection  = true
  username       = "administrator@vsphere.local"
  password     = "123Cisco123!"
  vcenter_server = "vc1.cam.ciscolabs.com"
  vm_name        = "nkt-${local.timestamp}"
  ssh_username = "cisco"
  ssh_password = "123Cisco123"
  disk_controller_type = ["lsilogic"]

    storage {
      disk_size = 32000
      disk_thin_provisioned = true
      disk_controller_index = 0
  }
}

# a build block invokes sources and runs provisioning steps on them. The
# documentation for build blocks can be found here:
# https://www.packer.io/docs/templates/hcl_templates/blocks/build
build {
  sources = ["source.vsphere-clone.clone"]

  provisioner "shell" {
    inline = [
      "sudo apt update",
      "sudo apt upgrade",
      "sudo apt install -y python3-pip sshpass",
      "wget https://github.com/camrossi/akb/archive/refs/heads/main.zip",
      "unzip main.zip",
      "rm main.zip",
      "sudo pip3 install -Ur akb-main/requirements.txt",
      "sudo ansible-galaxy collection install cisco.aci",
      "wget http://192.168.66.120/nkt/nkt_template.ova -O akb-main/terraform/static/vm_templates/nkt_template.ova",
      "wget https://releases.hashicorp.com/terraform/1.1.6/terraform_1.1.6_linux_amd64.zip",
      "sudo rm -f /bin/terraform",
      "sudo unzip terraform_1.1.6_linux_amd64.zip  -d /bin",
      "rm terraform_1.1.6_linux_amd64.zip",
      "cd akb-main/terraform",
      "terraform init",
      "sudo cp /home/cisco/akb-main/packer/nkt.service /etc/systemd/system/nkt.service",
      "sudo systemctl enable  nkt.service && sudo systemctl start nkt.service", 
    ]
  }
}