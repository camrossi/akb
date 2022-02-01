import json
from logging import error
from flask import Flask, Response, request, render_template, redirect, flash
from logging.config import dictConfig
from turbo_flask import Turbo
import requests
import os
from pyaci import Node, options, filters
import ipaddress
from pyVmomi import vim
from pyVim import connect
import re
from shelljob import proc
from distutils.version import LooseVersion
from time import sleep
l3out = {}
vc = {}
apic = {}
cluster = {}
calico_nodes = ""


# app = Flask(__name__)
app = Flask(__name__, template_folder='./TEMPLATES/')
app.config['SECRET_KEY'] = 'cisco'
turbo = Turbo(app)


def createl3outVars(l3out_tenant, name, vrf_name, physical_dom, mtu, ipv4_cluster_subnet, ipv6_cluster_subnet, def_ext_epg, import_security, shared_security, shared_rtctrl, local_as, bgp_pass, contract, dns_servers, dns_domain, anchor_nodes):
    def_ext_epg_scope = []
    floating_ip = ""
    secondary_ip = ""
    floating_ipv6 = ""
    secondary_ipv6 = ""
    if import_security:
        def_ext_epg_scope.append(import_security)
    if shared_rtctrl:
        def_ext_epg_scope.append(shared_rtctrl)
    if shared_security:
        def_ext_epg_scope.append(shared_security)
    try:
        floating_ip = str(ipaddress.IPv4Network(
            ipv4_cluster_subnet, strict=False).broadcast_address - 1)+ "/" + str(ipaddress.IPv4Network(ipv4_cluster_subnet, strict=False).prefixlen)
        secondary_ip = str(ipaddress.IPv4Network( 
            ipv4_cluster_subnet, strict=False).broadcast_address - 2) + "/" + str(ipaddress.IPv4Network(ipv4_cluster_subnet, strict=False).prefixlen)
    except:
        pass
    try:
        floating_ipv6 = str(ipaddress.IPv6Network(
            ipv6_cluster_subnet, strict=False).broadcast_address - 1) + "/" + str(ipaddress.IPv6Network(
            ipv6_cluster_subnet, strict=False).prefixlen)
        
        secondary_ipv6 = str(ipaddress.IPv6Network(
            ipv6_cluster_subnet, strict=False).broadcast_address - 2) + "/" + str(ipaddress.IPv6Network(
            ipv6_cluster_subnet, strict=False).prefixlen)
    except:
        pass

    dns_servers = list(dns_servers.split(","))
    anchor_nodes = json.loads(anchor_nodes)
    l3out = {
            "name": name, 
            "l3out_tenant": l3out_tenant, 
            "vrf_tenant": vrf_name.split('/')[0], 
            "vrf_name": vrf_name.split('/')[1], 
            "node_profile_name": "node_profile_FL3out", 
            "int_prof_name": "int_profile_FL3out", 
            "int_prof_name_v6": "int_profile_v6_FL3out", 
            "physical_dom": physical_dom, 
            "floating_ipv6": floating_ipv6, 
            "secondary_ipv6": secondary_ipv6, 
            "floating_ip": floating_ip,
             "secondary_ip": secondary_ip, 
             "def_ext_epg": def_ext_epg, 
             "def_ext_epg_scope": def_ext_epg_scope, 
             "local_as": local_as, 
             "mtu": mtu, 
             "bgp_pass": bgp_pass, 
             "max_node_prefixes": "500", 
             'contract': contract.split('/')[1], 
             'contract_tenant': contract.split('/')[0], 
             "dns_servers": dns_servers, 
             "dns_domain": dns_domain, 
             "anchor_nodes": anchor_nodes, 
             "ipv4_cluster_subnet": ipv4_cluster_subnet, 
             "ipv6_cluster_subnet": str(ipaddress.IPv6Network(ipv6_cluster_subnet))}
    return l3out

def createVCVars(url, username, passw, dc, datastore, cluster, dvs, port_group, vm_template, vm_folder):
    vc = {"url": url, "username": username, "pass": passw, "dc": dc, "datastore": datastore, "cluster": cluster,
          "dvs": dvs, "port_group": port_group, "vm_template": vm_template, "vm_folder": vm_folder}
    return vc


def createClusterVars(control_plane_vip, node_sub, node_sub_v6, ipv4_pod_sub, ipv6_pod_sub, ipv4_svc_sub, ipv6_svc_sub, external_svc_subnet, external_svc_subnet_v6, kube_version, kubeadm_token, 
                        crio_version, crio_os, haproxy_image, keepalived_image, keepalived_router_id, timezone, docker_mirror, http_proxy_status, http_proxy, ntp_server, ubuntu_apt_mirror):
    cluster = { "control_plane_vip": control_plane_vip.split(":")[0],
                "vip_port": control_plane_vip.split(":")[1],
                "pod_subnet": ipv4_pod_sub, 
                "pod_subnet_v6": ipv6_pod_sub,
                "cluster_svc_subnet": ipv4_svc_sub,
                "cluster_svc_subnet_v6": ipv6_svc_sub,
                "external_svc_subnet": external_svc_subnet,
                "external_svc_subnet_v6": external_svc_subnet_v6,
                "ingress_ip": str(ipaddress.IPv4Interface(external_svc_subnet).ip + 1),
                "kubeadm_token": kubeadm_token,
                "node_sub": node_sub,
                "node_sub_v6": node_sub_v6,
                "ntp_server": ntp_server,
                "kube_version": kube_version,
                "crio_version": crio_version, 
                "OS_Version": crio_os, 
                "haproxy_image": haproxy_image, 
                "keepalived_image": keepalived_image, 
                "keepalived_router_id": keepalived_router_id,
                "time_zone": timezone, 
                "docker_mirror": docker_mirror, 
                "http_proxy_status": http_proxy_status if http_proxy_status else "", 
                "http_proxy": http_proxy,
                "ubuntu_apt_mirror" : ubuntu_apt_mirror
                }
    return cluster

#These two methods create a stream that is then fed to an iFrame to auto populate the content on the fly
@app.route('/tf_plan', methods=['GET', 'POST'])
def tf_plan():
        g = proc.Group()
        g.run(["bash", "-c", "terraform init -no-color && terraform plan -no-color -var-file='cluster.tfvars' -out='plan'" ])
        #p = g.run("ls")
        return Response( read_process(g), mimetype='text/event-stream' )

@app.route('/tf_apply', methods=['GET', 'POST'])
def tf_apply():
        g = proc.Group()
        g.run(["bash", "-c", "terraform apply -auto-approve -no-color plan" ])
        #p = g.run("ls")
        return Response( read_process(g), mimetype='text/event-stream' )


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        try: 
            tf_apic = {}
            tf_apic['username'] = apic["akb_user"]
            tf_apic['cert_name'] = apic["cert_name"]
            tf_apic['private_key'] = apic["private_key"]
            tf_apic['url'] = apic["url"]
            tf_apic['oob_ips'] = apic["oob_ips"]
            config = "apic =" + json.dumps(tf_apic, indent=4)
            config += "\nvc =" + json.dumps(vc, indent=4)
            config += "\nl3out =" + json.dumps(l3out, indent=4)
            config += "\ncalico_nodes =" + json.dumps(calico_nodes, indent=4)
            config += "\nk8s_cluster =" + json.dumps(cluster, indent=4)
            with open('cluster.tfvars', 'w') as f:
                f.write(config)      
        except:
            config = []

        return render_template('create.html', config=config)
    elif request.method == 'POST':
            req = request.form
            button = req.get("button")
            if button == "Previous":
                return redirect('/cluster')
            if button == "Update Config":
                config = req.get('config')
                with open('cluster.tfvars', 'w') as f:
                    f.write(config)
                return render_template('create.html', config=config)

@app.route('/calico_nodes', methods=['GET', 'POST'])
def calico_nodes():
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        global calico_nodes
        calico_nodes = []
        if button == "Next":
            calico_nodes = json.loads(req.get("calico_nodes"))
            return redirect('/cluster')
        if button == "Previous":
            return redirect('/vcenter')
        if button == "Add Node":
            if req.get("calico_nodes") != "":
                try:
                    calico_nodes = json.loads(req.get("calico_nodes"))
                except ValueError as e:
                    return calico_nodes_error(req.get("calico_nodes"), "Invalid JSON:" + str(e))
            hostname = req.get("hostname")
            ip = req.get("ip")
            ipv6 = req.get("ipv6")
            natip = req.get("natip")
            rack_id = req.get("rack_id")
            local_as = req.get("local_as")
            if not is_valid_hostname(hostname):
                return calico_nodes_error(calico_nodes, "Error: Ivalid Hostname")

            # Check IP addresses
            try:
                # Use the Netwrok to ensure that the mask is always present
                ipaddress.IPv4Network(ip, strict=False)
            except ValueError as e:
                return calico_nodes_error(req.get("calico_nodes"), "Primary IPv4 Error: " + str(e))

            if ipaddress.IPv4Network(ip, strict=False).broadcast_address == ipaddress.IPv4Interface(ip).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv4 can't be the broadcast address " + ip)
            if ipaddress.IPv4Network(ip, strict=False).network_address == ipaddress.IPv4Interface(ip).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv4 can't be the network address " + ip)
            if ipaddress.IPv4Interface(ip).ip not in ipaddress.IPv4Network(l3out["ipv4_cluster_subnet"]):
                return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv4 must be contained in the IPv4 Cluster Subnet: " + l3out["ipv4_cluster_subnet"])
            if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(l3out["floating_ip"]).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the floating_ip " + l3out["floating_ip"])
            if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(l3out["secondary_ip"]).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the secondary_ip " + l3out["secondary_ip"])

            try:
                # Use the Netwrok to ensure that the mask is always present
                ipaddress.IPv6Network(ipv6, strict=False)
            except ValueError as e:
                return calico_nodes_error(req.get("calico_nodes"), "Primary IPv6 Error: " + str(e))
            if ipaddress.IPv6Network(ipv6, strict=False).broadcast_address == ipaddress.IPv6Interface(ipv6).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv6 can't be the broadcast address " + ipv6)
            if ipaddress.IPv6Network(ipv6, strict=False).network_address == ipaddress.IPv6Interface(ipv6).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv6 can't be the network address " + ipv6)
            if ipaddress.IPv6Interface(ipv6).ip not in ipaddress.IPv6Network(l3out["ipv6_cluster_subnet"]):
                return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv6 must be contained in the IPv6 Cluster Subnet: " + l3out["ipv6_cluster_subnet"])
            if ipaddress.IPv6Interface(ipv6).ip == ipaddress.IPv6Interface(l3out["floating_ipv6"]).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the floating_ipv6 " + l3out["floating_ipv6"])
            if ipaddress.IPv6Interface(ipv6).ip == ipaddress.IPv6Interface(l3out["secondary_ipv6"]).ip:
                return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the secondary_ipv6 " + l3out["secondary_ipv6"])

            if rack_id == "":
                return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Rack is mandatory")

            missing_rack = True
            for anchor_node in l3out["anchor_nodes"]:
                if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(anchor_node['primary_ip']).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Calico Node IP overlaps with the primary IP of anchor node " + anchor_node['node_id'],)
                if ipaddress.IPv6Interface(ipv6).ip == ipaddress.IPv6Interface(anchor_node['primary_ipv6']).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Calico Node IPv6 overlaps with the primary IPv6 of anchor node " + anchor_node['node_id'])
                # Check that there is at least one switch in the same rack ID as the node I am adding
                if rack_id == anchor_node['rack_id']:
                    missing_rack = False
            if missing_rack:
                return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Rack ID does not match the Rack ID of any anchor nodes " + rack_id)

            if local_as == "":
                return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Local AS is mandatory")
            if local_as == l3out['local_as']:
                return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Local AS can't be the same as the ACI fabric " + local_as)

            # check that we do not add duplicate calico nodes:
            for calico_node in calico_nodes:

                if calico_node['hostname'] == hostname:
                    return calico_nodes_error(req.get("calico_nodes"), "Duplicated Hostname" + hostname)
                elif calico_node['ip'] == ip:
                    return calico_nodes_error(req.get("calico_nodes"), "Duplicated Node IPv4:" + ip)
                elif calico_node['ipv6'] == ipv6:
                    return calico_nodes_error(req.get("calico_nodes"), "Duplicated Node IPv6:" + ipv6)
                elif calico_node['local_as'] != local_as:
                    return calico_nodes_error(req.get("calico_nodes"), "Node local AS must be the same:" + local_as)

            calico_nodes.append({"hostname": hostname, "ip": ip,
                                "ipv6": ipv6,"natip": natip, "local_as": local_as, "rack_id": rack_id})

            if turbo.can_stream():
                return turbo.stream(
                    turbo.update(render_template('_calico_nodes.html', calico_nodes=json.dumps(calico_nodes, indent=4)),
                                 target='calico_nodes'))

    if request.method == 'GET':
        return render_template('calico_nodes.html', ipv4_cluster_subnet=l3out["ipv4_cluster_subnet"], ipv6_cluster_subnet=l3out["ipv6_cluster_subnet"])


def is_valid_hostname(hostname):
    if hostname == "":
        return False
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def calico_nodes_error(calico_nodes, error):
    if turbo.can_stream():
        return turbo.stream(
            turbo.update(render_template('_calico_nodes.html', calico_nodes=calico_nodes, error=error),
                         target='calico_nodes'))


def k8s_versions():
    versions = []
    with open('TEMPLATES/K8s_Packages', 'r') as f:
        lines = f.read()

    packages = lines.split("\n\n")
    for package in packages:
        if "Package: kubelet" in package:
            # This is the name
            # package.split('\n')[0:2][0].split(':')[1].strip()
            # This is the version
            # package.split('\n')[0:2][1].split(':')[1].strip()
            versions.append(package.split('\n')[0:2][1].split(':')[1].strip())
    return sorted(versions, key=LooseVersion, reverse=True)


class BetterIPv6Network(ipaddress.IPv6Network):

    def __add__(self, offset):
        """Add numeric offset to the IP."""
        new_base_addr = int(self.network_address) + offset
        return self.__class__((new_base_addr, self.prefixlen))

    def size(self):
        """Return network size."""
        return 1 << (self.max_prefixlen - self.prefixlen)


class BetterIPv4Network(ipaddress.IPv4Network):

    def __add__(self, offset):
        """Add numeric offset to the IP."""
        new_base_addr = int(self.network_address) + offset
        return self.__class__((new_base_addr, self.prefixlen))

    def size(self):
        """Return network size."""
        return 1 << (self.max_prefixlen - self.prefixlen)


@app.route('/cluster', methods=['GET', 'POST'])
def cluster():

    # app.logger.info(apic+apic_password+apic_username)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == None and req.get("kube_version"):
            crio_versions = req.get("kube_version").split(
                '.')[0] + '.' + req.get("kube_version").split('.')[1]
            # Pick the crio version from the kubernetes version
            if turbo.can_stream():
                return turbo.stream(
                    turbo.update(render_template('_crio_versions.html', crio_versions=crio_versions),
                                 target='crio'))
        if button == "Next":
            global cluster
            cluster = createClusterVars(req.get("control_plane_vip"), l3out['ipv4_cluster_subnet'], l3out['ipv6_cluster_subnet'], req.get("ipv4_pod_sub"), req.get("ipv6_pod_sub"), req.get("ipv4_svc_sub"), req.get("ipv6_svc_sub"),req.get("ipv4_ext_svc_sub"), req.get("ipv6_ext_svc_sub"),
            req.get("kube_version"), req.get("kubeadm_token"), req.get("crio_version"), req.get("crio_os"), 
            req.get("haproxy_image"), req.get("keepalived_image"), req.get("keepalived_router_id"), 
            req.get("timezone"), req.get("docker_mirror"), req.get("http_proxy_status"), req.get("http_proxy"), req.get("ntp_server"), req.get("ubuntu_apt_mirror"))
            return redirect('/create')
        elif button == "Previous":
            return redirect('/calico_nodes')
    if request.method == 'GET':
        api_ip = str(ipaddress.IPv4Interface(
            l3out['ipv4_cluster_subnet']).ip + 2)

        # Calculate Subnets
        ipv4_cluster_subnet = BetterIPv4Network(l3out['ipv4_cluster_subnet'])
        ipv6_cluster_subnet = BetterIPv6Network(l3out['ipv6_cluster_subnet'], strict=False)

        # Calculate POD Subnets
        ipv4_pod_sub = (ipv4_cluster_subnet + 1 * ipv4_cluster_subnet.size())
        ipv6_pod_sub = (ipv6_cluster_subnet + 1 * ipv6_cluster_subnet.size())

        # Calculate SVC Subnets (Cluster_IP) and 
        # make them smaller as K8s only accepts up to 108 for services 
        ipv4_svc_sub = (ipv4_cluster_subnet + 2 * ipv4_cluster_subnet.size())
        ipv6_svc_sub_iterator = (ipv6_cluster_subnet + 2 * ipv6_cluster_subnet.size()).subnets(new_prefix=108)
        ipv6_svc_sub = next(ipv6_svc_sub_iterator)
        # Calculate External SVC Subnets (Cluster_IP)
        ipv4_ext_svc_sub = (ipv4_cluster_subnet + 3 * ipv4_cluster_subnet.size())
        ipv6_ext_svc_sub = next(ipv6_svc_sub_iterator)

        return render_template('cluster.html', ipv4_cluster_subnet=l3out['ipv4_cluster_subnet'], ipv6_cluster_subnet=l3out['ipv6_cluster_subnet'], api_ip=api_ip, k8s_ver=k8s_versions(), ipv4_pod_sub=ipv4_pod_sub, ipv6_pod_sub=ipv6_pod_sub,
        ipv4_svc_sub=ipv4_svc_sub, ipv6_svc_sub=ipv6_svc_sub,
        ipv4_ext_svc_sub=ipv4_ext_svc_sub, ipv6_ext_svc_sub=ipv6_ext_svc_sub)


@app.route('/vcenterlogin', methods=['GET', 'POST'])
def vcenterlogin():
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            global vc
            vc = {"url": "",
                  "username": "",
                  "pass": "",
                  "dc": "",
                  "datastore": "",
                  "cluster": "",
                  "dvs": "",
                  "port_group": "",
                  "vm_template": "",
                  "vm_folder": "",
                  }
            vc["url"] = req.get("url")
            vc["username"] = req.get("username")
            vc["pass"] = req.get("pass")
            return redirect('/vcenter')
        if button == "Previous":
            return redirect('/l3out')
    if request.method == 'GET':
        return render_template('vcenter-login.html')


def get_all_objs(content, vimtype):
    obj = {}
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj


def find_pgs(obj, pgs):
    if isinstance(obj, vim.Datacenter):
        for child in obj.networkFolder.childEntity:
            if (isinstance(child, vim.DistributedVirtualSwitch)):
                pg_dvs = child.summary.name + "/"
                for pg in child.portgroup:
                    # Only accept access ports
                    if isinstance(pg.config.defaultPortConfig.vlan, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec):
                        vlan = "vlan-" + \
                            str(pg.config.defaultPortConfig.vlan.vlanId)
                        pgs.append(pg_dvs + pg.summary.name + "/" + vlan)
            elif(isinstance(child, vim.Folder)):
                find_pgs(child, pgs)
    elif isinstance(obj, vim.Folder):
        for child in obj.childEntity:
            if (isinstance(child, vim.DistributedVirtualSwitch)):
                pg_dvs = child.summary.name + "/"
                for pg in child.portgroup:
                    # Only accept access ports
                    if isinstance(pg.config.defaultPortConfig.vlan, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec):
                        vlan = "vlan-" + \
                            str(pg.config.defaultPortConfig.vlan.vlanId)
                        pgs.append(pg_dvs + pg.summary.name + "/" + vlan)
            elif(isinstance(child, vim.Folder)):
                find_pgs(child, pgs)


def find_vms(obj, vms):
    if isinstance(obj, vim.Datacenter):
        for child in obj.vmFolder.childEntity:
            if (isinstance(child, vim.VirtualMachine)):
                vms.append(child.name)
            elif(isinstance(child, vim.Folder)):
                find_vms(child, vms)
    elif isinstance(obj, vim.Folder):
        for child in obj.childEntity:
            if (isinstance(child, vim.VirtualMachine)):
                vms.append(child.name)
            elif(isinstance(child, vim.Folder)):
                find_vms(child, vms)


@app.route('/vcenter', methods=['GET', 'POST'])
def vcenter():
    dss = []
    dvss = []
    vm_templates = []
    vc_folders = []
    pgs = []
    clusters = []
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            vc["dc"] = req.get('dc')
            vc["datastore"] = req.get('datastore')
            vc["cluster"] = req.get('cluster')
            vc["dvs"] = req.get('port_group').split('/')[0]
            vc["port_group"] = req.get('port_group').split('/')[1]
            l3out['vlan_id'] = req.get(
                'port_group').split('/')[2].split('-')[1]
            vc["vm_template"] = req.get('vm_templates')
            vc["vm_folder"] = req.get('vm_folder')
            return redirect('/calico_nodes')
        elif button == "Previous":
            return redirect('/vcenterlogin')

        elif button == None and req.get("dc"):
            si = connect.SmartConnectNoSSL(
                host=vc["url"],  user=vc["username"], pwd=vc["pass"], port='443')
            content = si.RetrieveContent()
            dcs = get_all_objs(content, [vim.Datacenter])
            dc_name = req.get('dc')
            for dc in dcs:
                if dc.name == dc_name:
                    for ds in dc.datastore:
                        dss.append(ds.name)
                    find_pgs(dc, pgs)

                    for child in dc.hostFolder.childEntity:
                        if (isinstance(child, vim.ClusterComputeResource)):
                            clusters.append(child.name)

                    find_vms(dc, vm_templates)

                    # Get only 1st level folder
                    for child in dc.vmFolder.childEntity:
                        if (isinstance(child, vim.Folder)):
                            vc_folders.append(child.name)

            connect.Disconnect(si)
            vc_folders = sorted(vc_folders, key=str.lower)
            dss = sorted(dss, key=str.lower)
            dvss = sorted(dvss, key=str.lower)
            vm_templates = sorted(vm_templates, key=str.lower)
            vc_folders = sorted(vc_folders, key=str.lower)
            pgs = sorted(pgs, key=str.lower)
            clusters = sorted(clusters, key=str.lower)

            if turbo.can_stream():
                return turbo.stream(
                    turbo.replace(render_template('_vc_details.html', dss=dss, clusters=clusters, vm_templates=vm_templates, vc_folders=vc_folders, pgs=pgs),
                                  target='vc'))

    if request.method == 'GET':
        si = connect.SmartConnectNoSSL(
            host=vc["url"],  user=vc["username"], pwd=vc["pass"], port='443')
        content = si.RetrieveContent()
        dcs = get_all_objs(content, [vim.Datacenter])
        connect.Disconnect(si)
        return render_template('vcenter.html', dcs=dcs.values(), )


def anchor_node_error(anchor_nodes, error):
    if turbo.can_stream():
        return turbo.stream(
            turbo.update(render_template('_anchor_nodes.html', anchor_nodes=anchor_nodes, error=error),
                         target='anchor_nodes'))


@app.route('/l3out', methods=['GET', 'POST'])
def l3out():
    phys_dom = []
    tenants = []
    vrfs = ["Select a Tenant"]
    local_as = ""
    pod_ids = []
    nodes_id = []
    anchor_nodes = []
    contracts = ['select a tenant']
    home = os.path.expanduser("~")
    meta_path = home + '/.aci-meta/aci-meta.json'
    pyaci_apic = Node(apic['url'],aciMetaFilePath = meta_path)

    try:
        pyaci_apic.useX509CertAuth(apic['akb_user'],apic['cert_name'],apic['private_key'])
    except FileNotFoundError as e:
        flash(u'Private Key Not Found', 'error')
        return redirect('/login')
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            global l3out
            mtu = int(req.get("mtu"))
            if mtu < 1280 or mtu > 9000:
                return anchor_node_error(req.get("anchor_nodes"), "Error: Ivalid MTU, MTU must be >= 1280 and <= 9000")
            if req.get("anchor_nodes") == "":
                return anchor_node_error(req.get("anchor_nodes"), "At least one anchor node is required")
            try:
                anchor_nodes = json.loads(req.get("anchor_nodes"))
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), "Invalid JSON:" + str(e))
            if "l3out_tenant" not in req:
                return anchor_node_error(req.get("anchor_nodes"), "Please Select a Tenant from the First Drop Down at the top of the page")
            l3out = createl3outVars(req.get("l3out_tenant"), req.get("name"), req.get("vrf_name"), req.get("physical_dom"), req.get("mtu"), req.get("ipv4_cluster_subnet"), req.get("ipv6_cluster_subnet"), req.get("def_ext_epg"), req.get(
                "import-security"), req.get("shared-security"), req.get("shared-rtctrl"), req.get("local_as"), req.get("bgp_pass"), req.get("contract"), req.get("dns_servers"), req.get("dns_domain"), req.get("anchor_nodes"))
            return redirect('/vcenterlogin')
        # Then the post came from the L3OUT Tenant Select
        elif button == None and req.get("l3out_tenant"):
            vrfs = []
            contracts = []
            tenant = req.get("l3out_tenant")
            if tenant != "common":
                regex = ".*tn-common|tn-" + tenant + ".*"
            else:
                regex = ".*tn-common.*"

            fvCtxs = pyaci_apic.methods.ResolveClass('fvCtx').GET(
                **options.filter(filters.Wcard('fvCtx.dn', regex)))
            for fvCtx in fvCtxs:
                # Get the tenant field and drop the tn-
                tenant = fvCtx.dn.split('/')[1][3:]
                name = fvCtx.name
                vrfs.append(tenant + '/' + name)

            vzBrCP = pyaci_apic.methods.ResolveClass('vzBrCP').GET(
                **options.filter(filters.Wcard('fvCtx.dn', regex)))
            for vzBrCP in vzBrCP:
                # Get the tenant field and drop the tn-
                tenant = vzBrCP.dn.split('/')[1][3:]
                name = vzBrCP.name
                contracts.append(tenant + '/' + name)

            contracts = sorted(contracts, key=str.lower)
            if turbo.can_stream():
                return turbo.stream(
                    turbo.replace(render_template('_vrf.html', vrfs=vrfs, contracts=contracts),
                                  target='vrf'))
        elif button == "Add Node":
            if req.get("anchor_nodes") != "":
                try:
                    anchor_nodes = json.loads(req.get("anchor_nodes"))
                except ValueError as e:
                    return anchor_node_error(req.get("anchor_nodes"), "Invalid JSON:" + str(e))

            rack_id = req.get("rack_id")
            rtr_id = req.get("rtr_id")
            primary_ip = req.get("node_ipv4")
            primary_ipv6 = req.get("node_ipv6")
            # I check here also the other parameters

            for dns in req.get("dns_servers").split(','):
                try:
                    # Use the Netwrok to ensure that the mask is always present
                    ipaddress.IPv4Address(dns)
                except ValueError as e:
                    return anchor_node_error(req.get("anchor_nodes"), "Invalid DNS Server: " + str(e))
            try:
                # Use the Netwrok to ensure that the mask is always present
                ipaddress.IPv4Network(
                    req.get("ipv4_cluster_subnet"), strict=False)
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), "IPv4 Cluster Subnet Error: " + str(e))

            try:
                # Use the Netwrok to ensure that the mask is always present
                ipaddress.IPv6Network(
                    req.get("ipv6_cluster_subnet"), strict=False)
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), "IPv6 Cluster Subnet Error: " + str(e))
            # vlan = int(req.get("vlan_id"))
            # if vlan == 0 or vlan > 4094:
            #    return anchor_node_error(req.get("anchor_nodes"), "Invalid VLAN ID")

            try:
                ipaddress.IPv4Address(rtr_id)
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), "Router ID Error: " + str(e))

            if ipaddress.IPv4Interface(primary_ip).ip not in ipaddress.IPv4Network(req.get("ipv4_cluster_subnet")):
                return anchor_node_error(req.get("anchor_nodes"), "The Primary IPv4 must be contained in the IPv4 Cluster Subnet")

            if ipaddress.IPv6Interface(primary_ipv6).ip not in ipaddress.IPv6Network(req.get("ipv6_cluster_subnet")):
                return anchor_node_error(req.get("anchor_nodes"), "The Primary IPv6 must be contained in the IPv6 Cluster Subnet")
            
            node_ipv4  = str(ipaddress.IPv4Interface(primary_ip).ip) + "/" + str(ipaddress.IPv4Network(req.get("ipv4_cluster_subnet")).prefixlen)
            node_ipv6  = str(ipaddress.IPv6Interface(primary_ipv6).ip) + "/" + str(ipaddress.IPv6Network(req.get("ipv6_cluster_subnet")).prefixlen)

            if rack_id == "":
                return anchor_node_error(req.get("anchor_nodes"), "Rack ID is required")

            # check that we do not add duplicate nodes:
            for anchor_node in anchor_nodes:

                if anchor_node['node_id'] == req.get("node_id"):
                    return anchor_node_error(req.get("anchor_nodes"), "Duplicated Node ID:" + req.get("node_id"))
                elif anchor_node['rtr_id'] == req.get("rtr_id"):
                    return anchor_node_error(req.get("anchor_nodes"), "Duplicated Router ID:" + req.get("rtr_id"))
                elif anchor_node['primary_ip'] == node_ipv4:
                    return anchor_node_error(req.get("anchor_nodes"), "Duplicated Node Primary IPv4:" + req.get("node_ipv4"))
                elif anchor_node['primary_ipv6'] == node_ipv6:
                    return anchor_node_error(req.get("anchor_nodes"), "Duplicated Node Primary IPv6:" + req.get("node_ipv6"))

            anchor_nodes.append({"pod_id": req.get("pod_id"), "rack_id": req.get("rack_id"), "node_id": req.get(
                "node_id"), "rtr_id": req.get("rtr_id"), "primary_ip": node_ipv4, "primary_ipv6": node_ipv6})

            if turbo.can_stream():
                return turbo.stream(
                    turbo.update(render_template('_anchor_nodes.html', anchor_nodes=json.dumps(anchor_nodes, indent=4)),
                                 target='anchor_nodes'))
        if button == "Previous":
            return redirect('/login')
    if request.method == 'GET':
       
        # Get required data from APIC:
        try:
            physDomPs = pyaci_apic.methods.ResolveClass('physDomP').GET()
        except:
            flash(u'Invalid Credentials', 'error')
            return redirect('/login')
        fvTenants = pyaci_apic.methods.ResolveClass('fvTenant').GET()
        local_as = pyaci_apic.mit.FromDn('uni/fabric/bgpInstP-default/as').GET()[0].asn
        pods = pyaci_apic.methods.ResolveClass('fabricPod').GET()
        nodes = pyaci_apic.methods.ResolveClass('fabricNode').GET(
            **options.filter(filters.Eq('fabricNode.role', 'leaf')))
        apics = pyaci_apic.methods.ResolveClass('topSystem').GET(**options.filter(filters.Eq('topSystem.role', 'controller')))
        for physDomP in physDomPs:
            phys_dom.append(physDomP.name)
        for fvTenant in fvTenants:
            tenants.append(fvTenant.name)
        for pod in pods:
            pod_ids.append(pod.id)
        for node in nodes:
            nodes_id.append(node.id)
        for a in apics:
            apic['oob_ips'] += (a.oobMgmtAddr) + ","
        #Remove the last comma
        apic['oob_ips'] = apic['oob_ips'][:-1]
        phys_dom = sorted(phys_dom, key=str.lower)
        tenants = sorted(tenants, key=str.lower)
        nodes_id = sorted(nodes_id, key=int)
        pod_ids = sorted(pod_ids, key=int)
        return render_template('l3out.html', phys_dom=phys_dom, tenants=tenants, vrfs=vrfs, local_as=local_as, pod_ids=pod_ids, nodes_id=nodes_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global apic
    apic = {}
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Login":
            apic['url'] = "https://" +  request.form['fabric']
            apic['username'] = request.form['username']
            apic['password'] = request.form['password']
            apic['akb_user'] = request.form['akb_user']
            apic['akb_pass'] = request.form['akb_pass']
            apic['private_key']= "../ansible/roles/aci/files/" + apic['akb_user'] + '-user.key'
            apic['cert_name'] = request.form['akb_user']
            apic['oob_ips'] = ""
            # PyACI requires to have the MetaData present locally. Since the metada changes depending on the APIC version I use an init container to pull it.
            # No you can't put it in the same container as the moment you try to import pyaci it crashed is the metadata is not there. Plus init containers are cool!
            # Get the APIC Model. s.environ.get("APIC_IPS").split(',')[0] gets me the first APIC here I don't care about RR
            url = apic['url'] + '/acimeta/aci-meta.json'
            try:
                r = requests.get(url, verify=False, allow_redirects=True, timeout=5)
            except:
                flash("Unable to connect to APIC", error)
                return render_template('login.html')
            home = os.path.expanduser("~")
            meta_path = home + '/.aci-meta'
            if not os.path.exists(meta_path):
                os.makedirs(meta_path)
            open(meta_path + '/aci-meta.json', 'wb').write(r.content) 
    ## Generate the inventory file for the APIC, this looks ugly might want to clean up
            config = f"""apic: #You ACI Fabric Name
  hosts:
    {request.form['fabric']}:
      validate_certs: no
      # APIC HTTPs Port 
      port: 443
      # APIC user with admin credential
      admin_user: {apic['username']}
      admin_pass: {apic['password']}
      # APIC User that we create only for the duration of this playbook
      # We also create certificates for this user name to use cert based authentication
      aci_temp_username: {apic['akb_user']}
      aci_temp_pass: {apic['akb_pass']}"""
            with open('../ansible/inventory/apic.yaml', 'w') as f:
                f.write(config)      
            # Generate temporary user and certificate
            g = proc.Group()
            g.run(["bash", "-c", "ansible-playbook -i ../ansible/inventory/apic.yaml ../ansible/apic_user.yaml"])
            #Just wait for terraform to finish
            while g.is_pending():
                lines = g.readlines()
            return redirect('/l3out')
        if button == "Previous":
            return redirect('/intro')
    return render_template('login.html')


def read_process(g):
    while g.is_pending():
        lines = g.readlines()
        for proc, line in lines:
            yield line          

@app.route('/existing_cluster', methods=['GET', 'POST'])
def existing_cluster():
    if request.method == "POST":
        g = proc.Group()
        g.run(["bash", "-c", "terraform destroy -auto-approve -no-color -var-file='cluster.tfvars'" ])

        #p = g.run("ls")
        return Response( read_process(g), mimetype= 'text/event-stream' )
    else:
        try:
            f = open("cluster.tfvars")
            # Do something with the file
        except IOError:
            return render_template('/existing_cluster.html', text_area_title="Error", config="Config File Not Found but terraform.tfstate file is present")
        
        return render_template('/existing_cluster.html', text_area_title="Cluster Config:", config=f.read())

@app.route('/')
@app.route('/intro', methods=['GET', 'POST'])
def get_page():
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Go":
            return redirect('/login')
    try:
        with open('terraform.tfstate', 'r') as f:
            state = json.load(f)
            # If there are resources the cluster is there
            if state['resources'] != []:
                return redirect('/existing_cluster')
            # If the resources are not present go to intro
            else:
                return render_template('intro.html')
    # If the state file is not there go to intro
    except:
         return render_template('intro.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
