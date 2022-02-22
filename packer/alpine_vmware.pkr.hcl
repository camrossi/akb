packer {
  required_plugins {
    vmware = {
      version = ">= 1.0.3"
      source = "github.com/hashicorp/vmware"
    }
  }
}
# The tempalte Need to have:
##apk add open-vm-tools open-vm-tools-guestinfo
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
  vm_name        = "nkt-${local.timestamp}"
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
      "echo 'https://mirror.aarnet.edu.au/pub/alpine/v3.15/main' > /etc/apk/repositories",
      "echo 'https://mirror.aarnet.edu.au/pub/alpine/v3.15/community' >> /etc/apk/repositories",
      "apk update",
      "apk upgrade",
      "apk add sshpass bash python3 py3-pip gcc python3-dev libressl-dev musl-dev libffi-dev libxml2-dev libxslt-dev make openssl-dev cargo",
      "wget https://github.com/camrossi/nkt/archive/refs/heads/main.zip",
      "unzip main.zip",
      "rm main.zip",
      "pip3 install -Ur nkt-main/requirements.txt",
      "ansible-galaxy collection install cisco.aci",
      "wget http://192.168.66.120/nkt/nkt_ubuntu21_template.ova -O nkt-main/terraform/static/vm_templates/nkt_ubuntu21_template.ova",
      "wget https://releases.hashicorp.com/terraform/1.1.3/terraform_1.1.3_linux_amd64.zip",
      "unzip terraform_1.1.3_linux_amd64.zip  -d /bin",
      "rm terraform_1.1.3_linux_amd64.zip",
      "cd /root/nkt-main/terraform",
      "terraform init",
      "rc-update add local default",
      "echo 'cd /root/nkt-main/terraform && python3 appflask.py 80 &' > /etc/local.d/nkt.start",
      "chmod +x /etc/local.d/nkt.start",
      "echo 'auto lo' > /etc/network/interfaces",
      "echo 'iface lo inet loopback' >> /etc/network/interfaces",
      "echo 'auto eth0' >> /etc/network/interfaces",
      "echo 'iface eth0 inet dhcp' >> /etc/network/interfaces",
      "echo 'https://dl-cdn.alpinelinux.org/alpine/v3.15/main' > /etc/apk/repositories",
      "echo 'https://dl-cdn.alpinelinux.org/alpine/v3.15/community' >> /etc/apk/repositories"
    ]
  }
}