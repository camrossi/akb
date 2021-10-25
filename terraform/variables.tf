variable "apic" {
  type = object({
  username          = string
  cert_name         = string
  private_key       = string
  url          = string
  })
  default = {
  username          = "admin"
  cert_name         = "admin.crt"
  private_key       = "../admin.key"
  url          = "https://10.48.170.201"
}
}

variable "vc" {
  type = object({
  url               = string
  username          = string
  pass              = string
  dc                = string
  datastore         = string
  cluster           = string
  dvs               = string
  port_group        = string
  vm_template       = string
  vm_folder         = string
  })
  default = {
  url               = "dom-vc02.cisco.com"
  username          = "administrator@dom.local"
  pass              = "C!sc0123"
  dc                = "DC1"
  datastore         = "datastorem4"
  cluster           = "Edge"
  dvs               = "vc02-DC1"
  port_group        = "vlan_k8s"
  vm_template       = "Ubuntu20.04"
  vm_folder         = "Demo"
}
}

variable "l3out" {
  type = object({
    name              = string
    l3out_tenant      = string
    vrf_tenant        = string
    vrf_name          = string
    node_profile_name = string
    int_prof_name     = string
    int_prof_name_v6     = string
    physical_dom      = string
    floating_ipv6       = string
    secondary_ipv6      = string
    floating_ip       = string
    secondary_ip      = string
    vlan_id           = number
    def_ext_epg       = string
    def_ext_epg_scope = list(string)
    local_as          = number
    mtu               = number
    bgp_pass          = string
    max_node_prefixes = number
    contract          = string
    dns_servers       = list(string)
    dns_domain        = string
    anchor_nodes      = list(object({
      node_id         = number
      rtr_id          = string
      pod_id          = number
      primary_ip      = string
      primary_ipv6    = string
      rack_id         = string
    }))
  })
  default = {
  name              = "FL3outnew"
  l3out_tenant      = "common"
  vrf_tenant        = "common"
  vrf_name          = "k8sVRF"
  node_profile_name = "node_profile_FL3out"
  int_prof_name     = "int_profile_FL3out"
  int_prof_name_v6  = "int_profile_v6_FL3out"
  physical_dom      = "k8slab-pdom"
  floating_ipv6     = "2001:db8:42:00::253/56"
  secondary_ipv6    = "2001:db8:42:00::254/56"
  floating_ip       = "192.168.2.253/24"
  secondary_ip      = "192.168.2.254/24"
  vlan_id           = 770
  def_ext_epg       = "catch_all"
  def_ext_epg_scope = ["import-security", "shared-security", "shared-rtctrl" ]
  local_as          = 65534
  mtu               = 9000
  bgp_pass          = "123Cisco123"
  max_node_prefixes = 500
  contract          = "k8s"
  dns_servers       = ["10.48.170.50","144.254.71.184"]
  dns_domain        = "k8s.cisco.com"
  anchor_nodes      = [
      {
      node_id         = 101
      pod_id          = 1
      rtr_id          = "1.1.4.201"
      primary_ip      = "192.168.2.101/24"
      primary_ipv6    = "2001:db8:42::201/56"
      rack_id         = "1"
      },
      {
      node_id         = 102
      pod_id          = 1
      rtr_id          = "1.1.4.202"
      primary_ip      = "192.168.2.102/24"
      rack_id         = "1"
      primary_ipv6    = "2001:db8:42::202/56"
      }
  ]
  }
}

variable "calico_nodes" {
  type = list(object({
    hostname        = string
    ip              = string
    ipv6            = string
    natip           = string
    local_as        = number
    rack_id         = string
     }))
  default = [
  {
      "hostname"        = "master-1"
      "ip"              = "192.168.2.1/24"
      "natip"           = "10.48.170.112"
      "local_as"        = "64501"
      ipv6              = "2001:db8:42::1/56"
      rack_id           = "1"
   },
   {
      "hostname"        = "master-2"
      "ip"              = "192.168.2.2/24"
      "natip"           = "10.48.170.113"      
      "local_as"        = "64502"
      ipv6              = "2001:db8:42::2/56"
      rack_id           = "1"
   },
   {
      "hostname"        = "master-3"
      "ip"              = "192.168.2.3/24"
      "natip"           = "10.48.170.114"      
      "local_as"        = "64503"
      ipv6              = "2001:db8:42::3/56"
      rack_id           = "1"
   },
   {
      "hostname"        = "worker-1"
      "ip"              = "192.168.2.4/24"
      "natip"           = "10.48.170.115"      
      "local_as"        = "64504"
      ipv6              = "2001:db8:42::4/56"
      rack_id           = "1"
   },
   {
      "hostname"        = "worker-2"
      "ip"              = "192.168.2.5/24"
      "natip"           = "10.48.170.116"      
      "local_as"        = "64505"
      ipv6              = "2001:db8:42::5/56"
      rack_id           = "1"
   },
   {
      "hostname"        = "worker-3"
      "ip"              = "192.168.2.6/24"
      "natip"           = "10.48.170.117"      
      "local_as"        = "64506"
      ipv6              = "2001:db8:42::6/56"
      rack_id           = "1"
   }
]
}

variable "k8s_cluster" {
  type = object({
    kube_version        = string
    crio_version        = string
    OS_Version          = string
    control_plane_vip   = string
    vip_port            = number
    haproxy_image       = string
    keepalived_image    = string
    keepalived_router_id= string
    kubeadm_token       = string
    node_sub            = string
    node_sub_v6         = string
    pod_subnet          = string
    pod_subnet_v6       = string
    cluster_svc_subnet  = string
    cluster_svc_subnet_v6  = string
    external_svc_subnet = string
    external_svc_subnet_v6 = string
    ingress_ip          = string
    ntp_server          = string
    time_zone           = string
    docker_mirror       = string
    http_proxy_status   = string
    http_proxy          = string

     })
  default = {
  kube_version        = "1.22.1-00"
  crio_version        = "1.21"
  OS_Version          = "xUbuntu_20.04"
  control_plane_vip   = "192.168.2.100"
  vip_port            = 8443
  haproxy_image       = "haproxy:2.3.6"
  keepalived_image    = "osixia/keepalived:2.0.20"
  keepalived_router_id= "51"
  kubeadm_token       = "fqv728.htdmfzf6rt9blhej"
  # specify new variable with a range in the node subnet to be used by ACI nodes - exclusion range
  node_sub            = "192.168.2.0/24"
  node_sub_v6         = "2001:db8:42::/56"  
  pod_subnet          = "10.1.0.0/16"
  pod_subnet_v6          = "2001:db8:43::/56"  
  cluster_svc_subnet  = "192.168.8.0/22"
  cluster_svc_subnet_v6  = "2001:db8:44:1::/112"  
  external_svc_subnet = "192.168.3.0/24"
  external_svc_subnet_v6 = "2001:db8:44:2::/112"
  ingress_ip          = "192.168.3.1"
  ntp_server          = "clock.cisco.com"
  time_zone           = "Europe/Rome"
  docker_mirror       = "10.67.185.120:5000"
  #if the k8s cluster should use a proxy to connect to internet, http_proxy_status should be set to enabled and the http_proxy should be specified
  http_proxy_status   = "enabled" 
  #http_proxy should be expressed as proxy_ip:port or proxy_fqdn:port
  http_proxy          = "proxy.esl.cisco.com:8080"
}
}