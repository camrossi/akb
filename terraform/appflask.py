from distutils.util import strtobool
import json
import sys
from logging import error
from flask import Flask, Response, request, render_template, redirect, flash, session
import vc_utils
from logging.config import dictConfig
from turbo_flask import Turbo
import requests
import os
from pyaci import Node, options, filters
import ipaddress
import re
from shelljob import proc
from distutils.version import LooseVersion
import random
import string
from datetime import datetime
import concurrent.futures
import hcl
from ndfc import NDFC, Fabric
from jinja2 import Template

# app = Flask(__name__)
app = Flask(__name__, template_folder='./TEMPLATES/')
app.config['SECRET_KEY'] = 'cisco'
turbo = Turbo(app)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_fabric_type(request: request) -> str:
    # get fabric type from url parameters
    fabric_type = request.args.get("fabric_type", None)
    if not fabric_type:
        fabric_type = "aci"
    return fabric_type.lower()


def normalize_url(hostname: str) -> str:
    if hostname.startswith('http://'):
        url = hostname.replace("http://", "https://")
    else:
        url = "https://" + hostname
    if url.endswith('/'):
        url = url[:-1]
    return url


def process_fabric_setting(data: dict) -> bool:
    global overlay
    global ipv6_enabled
    overlay = {}
    try:
        overlay["fabric_name"] = data["fabric_name"]
        overlay["asn"] = data["asn"]
        overlay["vrf"] = data["vrf"]
        overlay["loopback_ipv4"] = data["loopback_ipv4"]
        overlay["loopback_ipv6"] = data["loopback_ipv6"]
        overlay["gateway_v4"] = data["gateway_v4"]
        overlay["gateway_v6"] = data["gateway_v6"]
        overlay["node_sub"] = data["node_sub"]
        overlay["node_sub_v6"] = data["node_sub_v6"]
        overlay["dns_domain"] = data["dns_domain"]
        overlay["dns_servers"] = data["dns_servers"]
        overlay["ipv6_enabled"] = data["ipv6_enabled"]
        overlay["network"] = data["network"]
        overlay["ibgp_peer_vlan"] = data["ibgp_peer_vlan"]
        overlay["bgp_pass"] = data["bgp_pass"]
        overlay["k8s_route_map"] = data["k8s_route_map"]
        overlay["route_tag"] = data["route_tag"]
        overlay["vpc_peers"] = []
        for peer in data["vpc_peers"]:
            primary = {
                "hostname": peer["primary"],
                "loopback_id": data["loopback_id"],
                "loopback_ipv4": data["loopback_ipv4"][0],
                "loopback_ipv6": data["loopback_ipv6"][0] if overlay["ipv6_enabled"] else "",
                "ibgp_svi_ipv4": peer["primary_ipv4"],
                "ibgp_peer_ipv4": peer["secondary_ipv4"].split("/")[0],
                "ibgp_svi_ipv6": "",
                "ibgp_peer_ipv6": ""
            }

            secondary = {
                "hostname": peer["secondary"],
                "loopback_id": data["loopback_id"],
                "loopback_ipv4": data["loopback_ipv4"][1],
                "loopback_ipv6": data["loopback_ipv6"][1] if overlay["ipv6_enabled"] else "",
                "ibgp_svi_ipv4": peer["secondary_ipv4"],
                "ibgp_peer_ipv4": peer["primary_ipv4"].split("/")[0],
                "ibgp_svi_ipv6": "",
                "ibgp_peer_ipv6": ""
            }

            overlay["vpc_peers"].append([primary, secondary])
            ipv6_enabled = overlay["ipv6_enabled"]
    except KeyError as e:
        print(e)
        return False
    return True


def create_tf_vars(fabric_type: str,
                   vc: dict,
                   ndfc: dict,
                   overlay: dict,
                   calico_nodes: dict,
                   cluster: dict) -> str:
    with open("TEMPLATES/cluster_ndfc.tfvar.j2", "r") as f:
        tf_template = Template(f.read())
    tf_vars = tf_template.render(fabric_type=fabric_type,
                                 vc=vc,
                                 ndfc=ndfc,
                                 overlay=overlay,
                                 calico_nodes=calico_nodes,
                                 cluster=cluster)
    return tf_vars


def createl3outVars(l3out_tenant, name, vrf_name, physical_dom, mtu, ipv4_cluster_subnet, ipv6_cluster_subnet, def_ext_epg, import_security, shared_security, shared_rtctrl, local_as, bgp_pass, contract, anchor_nodes):
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
            ipv4_cluster_subnet, strict=False).broadcast_address - 1) + "/" + str(ipaddress.IPv4Network(ipv4_cluster_subnet, strict=False).prefixlen)
        secondary_ip = str(ipaddress.IPv4Network(
            ipv4_cluster_subnet, strict=False).broadcast_address - 2) + "/" + str(ipaddress.IPv4Network(ipv4_cluster_subnet, strict=False).prefixlen)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
        print(e)
        pass
    if ipv6_enabled:
        try:
            floating_ipv6 = str(ipaddress.IPv6Network(
                ipv6_cluster_subnet, strict=False).broadcast_address - 1) + "/" + str(ipaddress.IPv6Network(
                    ipv6_cluster_subnet, strict=False).prefixlen)

            secondary_ipv6 = str(ipaddress.IPv6Network(
                ipv6_cluster_subnet, strict=False).broadcast_address - 2) + "/" + str(ipaddress.IPv6Network(
                    ipv6_cluster_subnet, strict=False).prefixlen)
            ipv6_cluster_subnet = str(ipaddress.IPv6Network(ipv6_cluster_subnet))
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
            print(e)
            pass

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
        "anchor_nodes": anchor_nodes,
        "ipv4_cluster_subnet": ipv4_cluster_subnet,
        "ipv6_cluster_subnet": ipv6_cluster_subnet,
        "ipv6_enabled": ipv6_enabled
    }
    return l3out

def createVCVars(url="", username="", passw="", dc="", datastore="", cluster="", dvs="", port_group="", vm_template="", vm_folder="", vm_deploy=True):
    return {"url": url, "username": username, "pass": passw, "dc": dc, "datastore": datastore, "cluster": cluster,
          "dvs": dvs, "port_group": port_group, "vm_template": vm_template, "vm_folder": vm_folder, "vm_deploy": vm_deploy}
     


def createClusterVars(control_plane_vip="", node_sub="", node_sub_v6="", ipv4_pod_sub="", ipv6_pod_sub="", ipv4_svc_sub="", ipv6_svc_sub="", external_svc_subnet="", external_svc_subnet_v6="", local_as="", kube_version="", kubeadm_token="", 
                        crio_version="", crio_os="", haproxy_image="", keepalived_image="", keepalived_router_id="", timezone="", docker_mirror="", http_proxy_status="", http_proxy="", ntp_server="", ubuntu_apt_mirror="", sandbox_status="", eBPF_status="", dns_servers="", dns_domain=""):
    try:
        ingress_ip = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 1)
        visibility_ip = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 2)
        neo4j_ip = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 3)
    except:
        ingress_ip = ""
        visibility_ip = ""
        neo4j_ip = ""
    dns_servers = list(dns_servers.split(","))
    cluster = { "control_plane_vip": control_plane_vip.split(":")[0] if control_plane_vip != "" else "",
                "vip_port": control_plane_vip.split(":")[1] if control_plane_vip != "" else None,
                "pod_subnet": ipv4_pod_sub, 
                "pod_subnet_v6": ipv6_pod_sub,
                "cluster_svc_subnet": ipv4_svc_sub,
                "cluster_svc_subnet_v6": ipv6_svc_sub,
                "external_svc_subnet": external_svc_subnet,
                "external_svc_subnet_v6": external_svc_subnet_v6,
                "local_as" : local_as,
                "ingress_ip": ingress_ip,
                "visibility_ip": visibility_ip,
                "neo4j_ip": neo4j_ip,
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
                "ubuntu_apt_mirror" : ubuntu_apt_mirror,
                "sandbox_status" : True if sandbox_status == "on" else False,
                "eBPF_status" : True if eBPF_status == "on" else False,
                "dns_domain" : dns_domain,
                "dns_servers" : dns_servers
                } 
    return cluster

### DOCUMENTATION START ####


@app.route('/docs/doc', methods=['GET', 'POST'])
def docs():
    if request.method == 'POST':
        return redirect('/docs/prereqaci')
    return render_template('docs/doc.html')


@app.route('/docs/prereqaci', methods=['GET', 'POST'])
def prereqaci():
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Back":
            return redirect('/docs/doc')
        if button == "Next":
            return redirect('/docs/prereqvc')
    return render_template('docs/prereqaci.html')


# temporary solution for static page
@app.route('/docs/ndfc', methods=['GET', 'POST'])
def doc_ndfc():
    return render_template('docs/ndfc.html')

##### DOCUMENTATION END #####


# These two methods create a stream that is then fed to an iFrame to auto populate the content on the fly
@app.route('/tf_plan', methods=['GET', 'POST'])
def tf_plan():
    fabric_type = get_fabric_type(request)
    g = proc.Group()
    
    # Get the current dir
    cwd = os.getcwd()
    if fabric_type == "aci":
        with open("cluster.tfvars", 'r') as fp:
            current_config = hcl.load(fp)
        if not current_config['vc']['vm_deploy']:
            #Change to the VM module directory
            os.chdir("modules/k8s_node")
            if os.path.exists("vms.tf"):
                os.rename("vms.tf","vms.tf.ignore")
            if os.path.exists("outputs.tf"):
                os.rename("outputs.tf","outputs.tf.ignore")
            os.chdir(cwd)
        if current_config['vc']['vm_deploy']:
            os.chdir("modules/k8s_node")
            if os.path.exists("vms.tf.ignore"):
                os.rename("vms.tf.ignore","vms.tf")
            if os.path.exists("outputs.tf.ignore"):
                os.rename("outputs.tf.ignore","outputs.tf")
            os.chdir(cwd)
        if not os.path.exists('.terraform'):     
            g.run(["bash", "-c", "terraform init -no-color && terraform plan -no-color -var-file='cluster.tfvars' -out='plan'" ])
        else:
            g.run(["bash", "-c", "terraform plan -no-color -var-file='cluster.tfvars' -out='plan'"])
    elif fabric_type == "vxlan_evpn":
        if not os.path.exists('.terraform'):
            g.run(["bash", "-c", "terraform -chdir=ndfc init -no-color && terraform -chdir=ndfc plan -no-color -var-file='cluster.tfvars' -out='plan'"])
        else:
            g.run(["bash", "-c", "terraform -chdir=ndfc plan -no-color -var-file='cluster.tfvars' -out='plan'"])
    # p = g.run("ls")
    return Response(read_process(g), mimetype='text/event-stream')


@app.route('/tf_apply', methods=['GET', 'POST'])
def tf_apply():
    fabric_type = get_fabric_type(request)
    g = proc.Group()
    if fabric_type == "aci":
        g.run(["bash", "-c", "terraform apply -auto-approve -no-color plan" ])
    elif fabric_type == "vxlan_evpn":
        g.run(["bash", "-c", "terraform -chdir=ndfc apply -auto-approve -no-color plan"])
    return Response( read_process(g), mimetype='text/event-stream' )



@app.route('/create', methods=['GET', 'POST'])
def create():
    global cluster
    global apic
    global l3out
    global vc
    fabric_type = get_fabric_type(request)
    if request.method == 'GET':
        if fabric_type == "aci":
            try:
                tf_apic = {}
                tf_apic['username'] = apic["nkt_user"]
                tf_apic['cert_name'] = apic["nkt_user"]
                tf_apic['private_key'] = apic["private_key"]
                tf_apic['url'] = apic["url"]
                tf_apic['oob_ips'] = apic["oob_ips"]
                config = "apic =" + json.dumps(tf_apic, indent=4)
                config += "\nl3out =" + json.dumps(l3out, indent=4)
                if vc['vm_deploy']:
                    config += "\ncalico_nodes =" + json.dumps(calico_nodes, indent=4)
                else:
                    config += "\ncalico_nodes = null"
                config += "\nvc =" + json.dumps(vc, indent=4)
                config += "\nk8s_cluster =" + json.dumps(cluster, indent=4)
                with open('cluster.tfvars', 'w') as f:
                    f.write(config)
            except(KeyError, json.JSONDecodeError) as e:
                print(e)
                config = []
        elif fabric_type == "vxlan_evpn":
            try:
                config = create_tf_vars(fabric_type,
                                        vc,
                                        ndfc,
                                        overlay,
                                        calico_nodes,
                                        cluster)
                with open('./ndfc/cluster.tfvars', 'w') as f:
                    f.write(config)
            except Exception as e:
                print(e)
                config = []
        else:
            config = json.dumps({
                "error": "fabric_type is invalid, chosse between aci and vxlan_evpn"
            })
        return render_template('create.html', config=config)
    elif request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Previous":
            return redirect('/cluster?fabric_type=' + fabric_type)
        if button == "Update Config":
            config = req.get('config')
            with open('cluster.tfvars', 'w') as f:
                f.write(config)
            return render_template('create.html', config=config)


@app.route('/update_config', methods=['GET', 'POST'])
def update_config():
    fabric_type = get_fabric_type(request)
    if request.method == "POST":
        if fabric_type == "aci":
            config = request.json.get("config", "[]")
            with open('cluster.tfvars', 'w') as f:
                f.write(config)
            return json.dumps({"msg": "Config update success!"}), 200
        elif fabric_type == "vxlan_evpn":
            config = request.json.get("config", "[]")
            with open('./ndfc/cluster.tfvars', 'w') as f:
                f.write(config)
            return json.dumps({"msg": "Config update success!"}), 200
        else:
            return json.dumps({"error": "invalid fabric type"}), 400


@app.route('/calico_nodes', methods=['GET', 'POST'])
def calico_nodes():
    fabric_type = get_fabric_type(request)
    global calico_nodes
    calico_nodes = []
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            calico_nodes = json.loads(req.get("calico_nodes"))
            return redirect(f"/cluster?fabric_type={fabric_type}")
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
            print(hostname)
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
            if fabric_type == "aci":
                if ipaddress.IPv4Interface(ip).ip not in ipaddress.IPv4Network(l3out["ipv4_cluster_subnet"]):
                    return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv4 must be contained in the IPv4 Cluster Subnet: " + l3out["ipv4_cluster_subnet"])
                if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(l3out["floating_ip"]).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the floating_ip " + l3out["floating_ip"])
                if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(l3out["secondary_ip"]).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the secondary_ip " + l3out["secondary_ip"])
            elif fabric_type == "vxlan_evpn":
                if ipaddress.IPv4Interface(ip).ip not in ipaddress.IPv4Network(overlay["node_sub"]):
                    return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv4 must be contained in the selected Network Subnet: " + overlay["node_sub"])

            if ipv6_enabled:
                try:
                    # Use the Netwrok to ensure that the mask is always present
                    ipaddress.IPv6Network(ipv6, strict=False)
                except ValueError as e:
                    return calico_nodes_error(req.get("calico_nodes"), "Primary IPv6 Error: " + str(e))
                if ipaddress.IPv6Network(ipv6, strict=False).broadcast_address == ipaddress.IPv6Interface(ipv6).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv6 can't be the broadcast address " + ipv6)
                if ipaddress.IPv6Network(ipv6, strict=False).network_address == ipaddress.IPv6Interface(ipv6).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv6 can't be the network address " + ipv6)
                if fabric_type == "aci":
                    if ipaddress.IPv6Interface(ipv6).ip not in ipaddress.IPv6Network(l3out["ipv6_cluster_subnet"]):
                        return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv6 must be contained in the IPv6 Cluster Subnet: " + l3out["ipv6_cluster_subnet"])
                    if ipaddress.IPv6Interface(ipv6).ip == ipaddress.IPv6Interface(l3out["floating_ipv6"]).ip:
                        return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the floating_ipv6 " + l3out["floating_ipv6"])
                    if ipaddress.IPv6Interface(ipv6).ip == ipaddress.IPv6Interface(l3out["secondary_ipv6"]).ip:
                        return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the secondary_ipv6 " + l3out["secondary_ipv6"])
                elif fabric_type == "vxlan_evpn":
                    if ipaddress.IPv6Interface(ipv6).ip not in ipaddress.IPv6Network(overlay["node_sub_v6"]):
                        return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv6 must be contained in the Selected Network Subnet: " + overlay["node_sub_v6"])

            if rack_id == "":
                return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Rack is mandatory")

            missing_rack = True
            if fabric_type == "aci":
                for anchor_node in l3out["anchor_nodes"]:
                    if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(anchor_node['ip']).ip:
                        return calico_nodes_error(req.get("calico_nodes"), "The Calico Node IP overlaps with the primary IP of anchor node " + anchor_node['node_id'],)
                    if ipv6_enabled:
                        if ipaddress.IPv6Interface(ipv6).ip == ipaddress.IPv6Interface(anchor_node['ipv6']).ip:
                            return calico_nodes_error(req.get("calico_nodes"), "The Calico Node IPv6 overlaps with the primary IPv6 of anchor node " + anchor_node['node_id'])
                    # Check that there is at least one switch in the same rack ID as the node I am adding
                    if rack_id == anchor_node['rack_id']:
                        missing_rack = False
                if missing_rack:
                    return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Rack ID does not match the Rack ID of any anchor nodes " + rack_id)


            #if local_as == "":
            #    return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Local AS is mandatory")
            #if local_as == l3out['local_as']:
            #    return calico_nodes_error(req.get("calico_nodes"), "The Calico Node Local AS can't be the same as the ACI fabric " + local_as)

            # check that we do not add duplicate calico nodes:
            for calico_node in calico_nodes:

                if calico_node['hostname'] == hostname:
                    return calico_nodes_error(req.get("calico_nodes"), "Duplicated Hostname" + hostname)
                if calico_node['ip'] == ip:
                    return calico_nodes_error(req.get("calico_nodes"), "Duplicated Node IPv4:" + ip)
                if ipv6_enabled:
                    if calico_node['ipv6'] == ipv6:
                        return calico_nodes_error(req.get("calico_nodes"), "Duplicated Node IPv6:" + ipv6)

            calico_nodes.append({"hostname": hostname, "ip": ip,
                                "ipv6": ipv6, "natip": natip, "rack_id": rack_id})

            if turbo.can_stream():
                return turbo.stream(
                    turbo.update(render_template('_calico_nodes.html', calico_nodes=json.dumps(calico_nodes, indent=4)),
                                target='tf_calico_nodes'))

    if request.method == 'GET':
        if calico_nodes == []:
            i = 1
            while i <= 3:
                    hostname = 'nkt-master-' + str(i)
                    if fabric_type == "aci":
                        ip = str(ipaddress.IPv4Interface(l3out['ipv4_cluster_subnet']).ip + i) + "/" + str(ipaddress.IPv4Network(l3out["ipv4_cluster_subnet"]).prefixlen)
                    elif fabric_type == "vxlan_evpn":
                        host = str(ipaddress.IPv4Network(overlay['node_sub'])[i])
                        prefixlen = str(ipaddress.IPv4Network(overlay['node_sub']).prefixlen)
                        ip = f"{host}/{prefixlen}"
                    ipv6 = ""
                    natip = ""
                    rack_id = "1"
                    calico_nodes.append({"hostname": hostname, "ip": ip, "ipv6": ipv6,"natip": natip, "rack_id": rack_id})
                    i += 1
        if fabric_type == "aci":
            return render_template('calico_nodes.html', ipv4_cluster_subnet=l3out["ipv4_cluster_subnet"], ipv6_cluster_subnet=l3out["ipv6_cluster_subnet"], calico_nodes=json.dumps(calico_nodes, indent=4))
        elif fabric_type == "vxlan_evpn":
            return render_template('calico_nodes.html',
                                   ipv4_cluster_subnet=overlay["node_sub"],
                                   ipv6_cluster_subnet=overlay["node_sub_v6"],
                                   calico_nodes=json.dumps(calico_nodes, indent=4))


def is_valid_hostname(hostname):
    if hostname == "":
        return False
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[\-a-zA-Z0-9]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def calico_nodes_error(calico_nodes, error):
    if turbo.can_stream():
        return turbo.stream(
            turbo.update(render_template('_calico_nodes.html', calico_nodes=calico_nodes, error=error),
                         target='tf_calico_nodes'))


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
    fabric_type = get_fabric_type(request)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            global cluster
            if fabric_type == "aci":
                ipv4_cluster_subnet = l3out['ipv4_cluster_subnet']
                ipv6_cluster_subnet = l3out['ipv6_cluster_subnet']
            elif fabric_type == "vxlan_evpn":
                ipv4_cluster_subnet = overlay["node_sub"]
                ipv6_cluster_subnet = overlay["node_sub_v6"]
            crio_version = req.get("kube_version").split('.')[0] + '.' + req.get("kube_version").split('.')[1]
            cluster = createClusterVars(req.get("control_plane_vip"), ipv4_cluster_subnet, ipv6_cluster_subnet, req.get("ipv4_pod_sub"), req.get("ipv6_pod_sub"), req.get("ipv4_svc_sub"), 
            req.get("ipv6_svc_sub"), req.get("ipv4_ext_svc_sub"), req.get("ipv6_ext_svc_sub"), req.get("local_as"),req.get("kube_version"), req.get("kubeadm_token"), crio_version, req.get("crio_os"),
            req.get("haproxy_image"), req.get("keepalived_image"), req.get("keepalived_router_id"), req.get("timezone"), req.get("docker_mirror"), req.get("http_proxy_status"), 
            req.get("http_proxy"), req.get("ntp_server"), req.get("ubuntu_apt_mirror"), req.get("sandbox_status"),req.get("eBPF_status"),req.get("dns_servers"), req.get("dns_domain"))
            if fabric_type == "aci":
                return redirect('/cluster_network')
            elif fabric_type == "vxlan_evpn":
                return redirect(f'/cluster_network?fabric_type={fabric_type}')
        elif button == "Previous":
            return redirect('/calico_nodes')
    if request.method == 'GET':
        if fabric_type == "aci":
            ipv4_cluster_subnet = l3out['ipv4_cluster_subnet']
        elif fabric_type == "vxlan_evpn":
            ipv4_cluster_subnet = overlay["node_sub"]

        api_ip = str(ipaddress.IPv4Network(ipv4_cluster_subnet, strict=False).broadcast_address - 3)

        return render_template('cluster.html', api_ip=api_ip, k8s_ver=k8s_versions())


@app.route('/cluster_network', methods=['GET', 'POST'])
def cluster_network():
    fabric_type = get_fabric_type(request)

    # app.logger.info(apic+apic_password+apic_username)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            if not vc['vm_deploy']:
                global cluster
                cluster = createClusterVars()
                l3out['vlan_id'] = req.get("vlan_id")
            external_svc_subnet = req.get("ipv4_ext_svc_sub")
            cluster['pod_subnet'] = req.get("ipv4_pod_sub")
            cluster['external_svc_subnet'] = external_svc_subnet
            cluster['cluster_svc_subnet'] = req.get("ipv4_svc_sub")
            cluster['local_as'] = req.get("k8s_local_as")
            cluster['ingress_ip'] = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 1)
            cluster['visibility_ip'] = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 2)
            cluster['neo4j_ip'] = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 3)
            if ipv6_enabled: 
                cluster['cluster_svc_subnet_v6'] = req.get("ipv6_svc_sub")
                cluster['pod_subnet_v6'] = req.get("ipv6_pod_sub")
                cluster['cluster_svc_subnet_v6'] = req.get("ipv6_svc_sub")
                cluster['external_svc_subnet_v6'] = req.get("ipv6_ext_svc_sub")
            else:
                cluster['cluster_svc_subnet_v6'] = ""
                cluster['pod_subnet_v6'] = ""
                cluster['cluster_svc_subnet_v6'] = ""
                cluster['external_svc_subnet_v6'] = ""
            
            return redirect(f'/create?fabric_type={fabric_type}')
        elif button == "Previous" and vc['vm_deploy']:
            return redirect(f'/cluster?fabric_type={fabric_type}')
        elif button == "Previous" and not vc['vm_deploy']:
            if fabric_type == "aci":
                return redirect('/l3out')
            elif fabric_type == "vxlan_evpn":
                return redirect('/fabric')
    if request.method == 'GET':
        if fabric_type == "aci":
            ipv4_cluster_subnet = l3out['ipv4_cluster_subnet']
            k8s_local_as= int(l3out['local_as'])+1
        elif fabric_type == "vxlan_evpn":
            ipv4_cluster_subnet = overlay['node_sub']
            k8s_local_as= int(overlay["asn"]) + 1

        # Calculate Subnets
        ipv4_cluster_subnet = BetterIPv4Network(ipv4_cluster_subnet)

        # Calculate POD Subnets
        ipv4_pod_sub = (ipv4_cluster_subnet + 1 * ipv4_cluster_subnet.size())

        # Calculate SVC Subnets (Cluster_IP) and
        # make them smaller as K8s only accepts up to 108 for services
        ipv4_svc_sub = (ipv4_cluster_subnet + 2 * ipv4_cluster_subnet.size())

        # Calculate External SVC Subnets (Cluster_IP)
        ipv4_ext_svc_sub = (ipv4_cluster_subnet + 3 * ipv4_cluster_subnet.size())

        #same as above just for v6
        ipv6_cluster_subnet = ""
        ipv6_pod_sub = ""
        ipv6_svc_sub = ""
        ipv6_ext_svc_sub = ""
        if ipv6_enabled:
            if fabric_type == "aci":
                ipv6_cluster_subnet = l3out['ipv6_cluster_subnet']
            elif fabric_type == "vxlan_evpn":
                ipv6_cluster_subnet = overlay["node_sub_v6"]
            ipv6_cluster_subnet = BetterIPv6Network(ipv6_cluster_subnet, strict=False)
            ipv6_pod_sub = (ipv6_cluster_subnet + 1 * ipv6_cluster_subnet.size())
            ipv6_svc_sub_iterator = (ipv6_cluster_subnet + 2 * ipv6_cluster_subnet.size()).subnets(new_prefix=108)
            ipv6_svc_sub = next(ipv6_svc_sub_iterator)
            ipv6_ext_svc_sub = next(ipv6_svc_sub_iterator)

        if fabric_type == "aci":
            return render_template('cluster_network.html', ipv4_cluster_subnet=l3out['ipv4_cluster_subnet'], ipv6_cluster_subnet=l3out['ipv6_cluster_subnet'], ipv4_pod_sub=ipv4_pod_sub, ipv6_pod_sub=ipv6_pod_sub,ipv4_svc_sub=ipv4_svc_sub, ipv6_svc_sub=ipv6_svc_sub, ipv4_ext_svc_sub=ipv4_ext_svc_sub, ipv6_ext_svc_sub=ipv6_ext_svc_sub, k8s_local_as=k8s_local_as, vm_deploy=vc['vm_deploy'])
        elif fabric_type == "vxlan_evpn":
            return render_template('cluster_network.html',
                                   ipv4_cluster_subnet=overlay["node_sub"],
                                   ipv6_cluster_subnet=overlay["node_sub_v6"],
                                   ipv4_pod_sub=ipv4_pod_sub,
                                   ipv6_pod_sub=ipv6_pod_sub,
                                   ipv4_svc_sub=ipv4_svc_sub,
                                   ipv6_svc_sub=ipv6_svc_sub,
                                   ipv4_ext_svc_sub=ipv4_ext_svc_sub,
                                   ipv6_ext_svc_sub=ipv6_ext_svc_sub,
                                   k8s_local_as=k8s_local_as,
                                   vm_deploy=vc['vm_deploy'])



@app.route('/vcenterlogin', methods=['GET', 'POST'])
def vcenterlogin():
    global vc
    fabric_type = get_fabric_type(request)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            vc = createVCVars()
            vc["url"] = req.get("url")
            vc["username"] = req.get("username")
            vc["pass"] = req.get("pass")
            if fabric_type == "aci":
                if req.get("template"):
                    return redirect('/vctemplate')
                return redirect('/vcenter')
            if fabric_type == "vxlan_evpn":
                return redirect(f"/vcenter?fabric_type={fabric_type}")
        if button == "Previous":
            if fabric_type == "aci":
                return redirect('/l3out')
            if fabric_type == "vxlan_evpn":
                return redirect(f"/fabric?fabric_type={fabric_type}")
    if request.method == 'GET':
        if fabric_type == "aci":
            return render_template('vcenter-login.html')
        if fabric_type == "vxlan_evpn":
            return render_template('vcenter-login.html', fabric_type=fabric_type)

@app.route('/vctemplate', methods=['GET', 'POST'])
def vctemplate():
    global vc
    vc_folders = []
    dss = []
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Previous":
            return redirect('/vcenterlogin')
        if button == None and req.get("dc"):
            si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
            dcs = vc_utils.get_all_dcs(si)
            dc_name = req.get('dc')
            for dc in dcs:
                if dc.name == dc_name:
                    for ds in dc.datastore:
                        dss.append(ds.name)
                    for child in dc.vmFolder.childEntity:
                        if vc_utils.find_folders(child):
                            vc_folders.append(child.name)
            
            vc_utils.disconnect(si)
            vc_folders = sorted(vc_folders, key=str.lower)
            dss = sorted(dss, key=str.lower)

            if turbo.can_stream():
                return turbo.stream(
                    turbo.update(render_template('_template_folder.html', vc_folders=vc_folders, dcs=dcs.values(),dss=dss),
                                  target='template-upload-folder'))

        if button == "Upload":
            template_name = "nkt_template"
            si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
            datacenter = vc_utils.get_dc(si, req.get('dc'))
            datastore = vc_utils.get_ds(datacenter, req.get('datastore'))
            resource_pool = vc_utils.get_largest_free_rp(si, datacenter)
            ova_path = str(os.getcwd()) + "/static/vm_templates/nkt_template.ova"
            ovf_handle = vc_utils.OvfHandler(ova_path)
            ovf_manager = si.content.ovfManager
            cisp = vc_utils.import_spec_params(entityName=template_name, diskProvisioning='thin')

            cisr = ovf_manager.CreateImportSpec(ovf_handle.get_descriptor(), resource_pool, datastore, cisp)
            if cisr.error:
                print("The following errors will prevent import of this OVA:")
                for error in cisr.error:
                    print("%s" % error)

            ovf_handle.set_spec(cisr)


            #Start upload as a new thread
            #Find Folder
            # Get only 1st level folder
            for child in datacenter.vmFolder.childEntity:
                if vc_utils.find_folders(child):
                    if child.name == req.get('vm_folder'):
                        folder = child

            # If the template already exists, delete it!
            vm = vc_utils.find_by_name(si,folder,template_name)
            if vm:
                task = vm.Destroy_Task()
                task.vc_utils.wait_for_tasks(si, [task])
            upload = concurrent.futures.ThreadPoolExecutor()
            upload.submit(vc_utils.start_upload, vc["url"], resource_pool,cisr, folder, ovf_handle)
            # Wait for upload to complete UI freeze here
            upload.shutdown(wait=True)
            vm = vc_utils.find_by_name(si,folder,template_name)
            vm.CreateSnapshot_Task(name=str(datetime.now()),
                                        description="Snapshot",
                                        memory=False,
                                        quiesce=False)

            return redirect('/vcenter')
            
            
    if request.method == 'GET':
        try:
            si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
        except Exception as e:
            flash(e.msg, 'error')
            return redirect('/vcenterlogin')

        dcs = vc_utils.get_all_dcs(si)
        vc_utils.disconnect(si)
        return render_template('vc_template_upload.html', dcs=dcs.values(), progress=0)

@app.route('/vcenter', methods=['GET', 'POST'])
def vcenter():
    fabric_type = get_fabric_type(request)
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
            if fabric_type == "aci":
                l3out['vlan_id'] = req.get('port_group').split('/')[2].split('-')[1]
            vc["vm_template"] = req.get('vm_templates')
            vc["vm_folder"] = req.get('vm_folder')
            if fabric_type == "vxlan_evpn":
                return redirect(f'/calico_nodes?fabric_type={fabric_type}')
            else:
                return redirect('/calico_nodes')
        elif button == "Previous":
            return redirect(f'/vcenterlogin?fabric_type={fabric_type}')

        elif button == None and req.get("dc"):
            si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
            dcs = vc_utils.get_all_dcs(si)
            dc_name = req.get('dc')
            for dc in dcs:
                if dc.name == dc_name:
                    for ds in dc.datastore:
                        dss.append(ds.name)
                    
                    vc_utils.find_pgs(dc, pgs)
                    for child in dc.hostFolder.childEntity:
                        if (vc_utils.find_compute_cluster(child)):
                            clusters.append(child.name)

                    vc_utils.find_vms(dc, vm_templates)

                    # Get only 1st level folder
                    for child in dc.vmFolder.childEntity:
                        if vc_utils.find_folders(child):
                            vc_folders.append(child.name)

            vc_utils.disconnect(si)
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
        try:
            si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
        except Exception as e:
            flash(e, 'error')
            return redirect('/vcenterlogin')

        dcs = vc_utils.get_all_dcs(si)
        vc_utils.disconnect(si)
        return render_template('vcenter.html', dcs=dcs.values(), fabric_type=fabric_type)


def anchor_node_error(anchor_nodes, pod_ids, nodes_id, rtr_id, error):
    if turbo.can_stream():
        return turbo.stream(
            turbo.update(render_template('_anchor_nodes.html', pod_ids=pod_ids, nodes_id=nodes_id, anchor_nodes=anchor_nodes, rtr_id=rtr_id, error=error),
                         target='anchor_nodes'))


@app.route('/l3out', methods=['GET', 'POST'])
def l3out():
    phys_dom = []
    tenants = []
    vrfs = ["Select a Tenant"]
    local_as = ""
    anchor_nodes = []
    contracts = ['select a tenant']
    home = os.path.expanduser("~")
    meta_path = home + '/.aci-meta/aci-meta.json'
    pyaci_apic = Node(apic['url'], aciMetaFilePath=meta_path)
    rtr_id_counter = ipaddress.IPv4Address("1.1.1.1")
    global ipv6_enabled
    try:
        pyaci_apic.useX509CertAuth(apic['nkt_user'],apic["nkt_user"],apic['private_key'])
    except FileNotFoundError as e:
        print(e)
        return redirect('/login')
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            global l3out
            mtu = int(req.get("mtu"))
            if mtu < 1280 or mtu > 9000:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Error: Ivalid MTU, MTU must be >= 1280 and <= 9000")
            if req.get("anchor_nodes") == "":
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "At least one anchor node is required")
            try:
                anchor_nodes = json.loads(req.get("anchor_nodes"))
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Invalid JSON:" + str(e))
            if "l3out_tenant" not in req:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Please Select a Tenant from the First Drop Down at the top of the page")
            
            # Ensure VRF is NOT configured with BD Enforcement
            fvCtx_dn = 'uni/tn-' + req.get("vrf_name").split('/')[0] +'/ctx-' + req.get("vrf_name").split('/')[1]
            if pyaci_apic.mit.FromDn(fvCtx_dn).GET()[0].bdEnforcedEnable == 'yes':
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Error: The VRF is configured with BD Enforcement. This will result in the eBGP peering not to form. Please Disable BD Enforcement under the VRF before continuing")

            l3out = createl3outVars(req.get("l3out_tenant"), req.get("name"), req.get("vrf_name"), req.get("physical_dom"), req.get("mtu"), req.get("ipv4_cluster_subnet"), req.get("ipv6_cluster_subnet"), req.get("def_ext_epg"), req.get(
                "import-security"), req.get("shared-security"), req.get("shared-rtctrl"), req.get("local_as"), req.get("bgp_pass"), req.get("contract"), req.get("anchor_nodes"))
            if vc['vm_deploy']:
                return redirect('/vcenterlogin')
            else:
                return redirect('/cluster_network')
        # Then the post came from the L3OUT Tenant Select
        elif button is None and req.get("l3out_tenant"):
            vrfs = []
            contracts = []
            tenant = req.get("l3out_tenant")
            if tenant != "common":
                regex = ".*tn-common|tn-" + tenant + "/.*"
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
        elif button == "Add Leaf":
            if req.get("anchor_nodes") != "":
                try:
                    anchor_nodes = json.loads(req.get("anchor_nodes"))
                except ValueError as e:
                    return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Invalid JSON:" + str(e))
            if req.get("ipv6_cluster_subnet") == "":
                ipv6_enabled = False
            else:
                ipv6_enabled = True
            rack_id = req.get("rack_id")
            rtr_id = req.get("rtr_id")
            primary_ip = req.get("node_ipv4")

            # I check here also the other parameters

            try:
                # Use the Netwrok to ensure that the mask is always present
                ipaddress.IPv4Network(
                    req.get("ipv4_cluster_subnet"), strict=False)
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "IPv4 Cluster Subnet Error: " + str(e))

            try:
                ipaddress.IPv4Address(rtr_id)
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Router ID Error: " + str(e))

            try:
                ipaddress.IPv4Interface(primary_ip)
            except ValueError as e:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Primary IPv4: " + str(e))

            if ipaddress.IPv4Interface(primary_ip).ip not in ipaddress.IPv4Network(req.get("ipv4_cluster_subnet")):
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "The Primary IPv4 must be contained in the IPv4 Cluster Subnet")

            if ipaddress.IPv4Interface(primary_ip).ip == ipaddress.IPv4Network(req.get("ipv4_cluster_subnet")).network_address:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "The Primary IPv4 is equal to the subnet address")

            if ipv6_enabled:
                primary_ipv6 = req.get("node_ipv6")
                try:
                    # Use the Netwrok to ensure that the mask is always present
                    ipaddress.IPv6Network(
                        req.get("ipv6_cluster_subnet"), strict=False)
                except ValueError as e:
                    return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "IPv6 Cluster Subnet Error: " + str(e))

                try:
                    ipaddress.IPv6Interface(primary_ipv6)
                except ValueError as e:
                    return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Primary IPv6: " + str(e))

                if ipaddress.IPv6Interface(primary_ipv6).ip not in ipaddress.IPv6Network(req.get("ipv6_cluster_subnet")):
                    return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "The Primary IPv6 must be contained in the IPv6 Cluster Subnet")

                node_ipv6 = str(ipaddress.IPv6Interface(primary_ipv6).ip) + "/" + str(ipaddress.IPv6Network(req.get("ipv6_cluster_subnet")).prefixlen)
            else:
                node_ipv6 = ""
            node_ipv4 = str(ipaddress.IPv4Interface(primary_ip).ip) + "/" + str(ipaddress.IPv4Network(req.get("ipv4_cluster_subnet")).prefixlen)

            if rack_id == "":
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Rack ID is required")

            # check that we do not add duplicate nodes:
            for anchor_node in anchor_nodes:

                if anchor_node['node_id'] == req.get("node_id"):
                    return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Duplicated Node ID:" + req.get("node_id"))
                if anchor_node['rtr_id'] == req.get("rtr_id"):
                    return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Duplicated Router ID:" + req.get("rtr_id"))
                if anchor_node['ip'] == node_ipv4:
                    return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Duplicated Node Primary IPv4:" + req.get("node_ipv4"))
                if ipv6_enabled:
                    if anchor_node['ipv6'] == node_ipv6:
                        return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Duplicated Node Primary IPv6:" + req.get("node_ipv6"))

            anchor_nodes.append({"pod_id": req.get("pod_id"), "rack_id": req.get("rack_id"), "node_id": req.get(
                "node_id"), "rtr_id": req.get("rtr_id"), "ip": node_ipv4, "ipv6": node_ipv6})
            if turbo.can_stream():
                return turbo.stream(
                    turbo.update(render_template('_anchor_nodes.html', pod_ids=session['pod_ids'], nodes_id=session['nodes_id'], rtr_id=str(rtr_id_counter + 1), anchor_nodes=json.dumps(anchor_nodes, indent=4)),
                                 target='anchor_nodes'))
        if button == "Previous":
            return redirect('/login')
    if request.method == 'GET':
        pod_ids = []
        nodes_id = []
        # Get required data from APIC:
        try:
            physDomPs = pyaci_apic.methods.ResolveClass('physDomP').GET()
        except Exception as e:
            print(e)
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
        session['nodes_id'] = sorted(nodes_id, key=int)
        session['pod_ids'] = sorted(pod_ids, key=int)
        return render_template('l3out.html', phys_dom=phys_dom, tenants=tenants, vrfs=vrfs, local_as=local_as, pod_ids=session['pod_ids'], nodes_id=session['nodes_id'], rtr_id=str(rtr_id_counter))


@app.route("/fabric", methods=["GET", "POST"])
def fabric():
    fabric_type = get_fabric_type(request)
    if "ndfc" not in globals():
        return redirect(f"/login?fabric_type={fabric_type}")
    if request.method == "GET":
        if fabric_type == "vxlan_evpn":
            fabrics = []
            inst_ndfc = NDFC(ndfc["url"], ndfc["username"], ndfc["password"])
            inst_ndfc.logon()
            result = inst_ndfc.get_fabrics()
            if result:
                for f in result:
                    fabric = {
                        "fabric_name": f.get("fabricName"),
                        "asn": f.get("asn")
                    }
                    fabrics.append(fabric)
            return render_template("fabric.html", fabrics=fabrics)
    if request.method == "POST":
        data = request.json
        result = process_fabric_setting(data)
        if result:
            return json.dumps({"ok": "fabric setting configured"}), 200
        else:
            return json.dumps({"error": "invalid settings"}), 400


@app.route("/query_ndfc", methods=["GET"])
def query_ndfc():
    # function to implement query ndfc API
    fabric_name = request.args.get("fabric_name")
    query_vrf = request.args.get("query_vrf")
    query_net = request.args.get("query_network")
    query_inv = request.args.get("query_inv")
    vrf_name = request.args.get("vrf_name")
    inst_ndfc = NDFC(ndfc["url"], ndfc["username"], ndfc["password"])
    logon = inst_ndfc.logon()
    if not logon:
        return json.dumps('{"error": "login failed"}'), 400
    if query_vrf == "true":
        vrfs = []
        result = inst_ndfc.get_vrfs(fabric_name)
        for vrf in result:
            vrfs.append(vrf["vrfName"])
        return json.dumps(vrfs), 200
    elif query_inv == "true":
        vpc_peers = []
        fabric = Fabric(fabric_name, inst_ndfc)
        fabric.get_inventory()
        inv = fabric.inventory
        for sw in inv.values():
            if not sw.get("isVpcConfigured") or sw.get("role").lower() != "primary":
                continue
            vpc = {
                "primary": sw.get("hostName"),
                "secondary": sw.get("peer")
            }
            vpc_peers.append(vpc)
        return json.dumps(vpc_peers), 200
    elif query_net == "true":
        networks = []
        fabric = Fabric(fabric_name, inst_ndfc)
        result = fabric.get_network_detail(vrf_name=vrf_name)
        if result:
            for item in result:
                subnet_v4 = str(ipaddress.IPv4Interface(item.gateway).network)
                subnet_v6 = str(ipaddress.IPv6Interface(item.gateway_v6).network) if item.gateway_v6 else ""
                net = {
                    "name": item.name,
                    "gateway_v4": item.gateway,
                    "gateway_v6": item.gateway_v6,
                    "subnet_v4": subnet_v4,
                    "subnet_v6": subnet_v6
                }
                networks.append(net)
        return json.dumps(networks), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    global apic
    apic = {}
    global vc
    vc = createVCVars()
    ansible_output = ''
    fabric_type = get_fabric_type(request)

    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Login":
            if request.form['fabric'].startswith('http://'):
                apic['url'] = request.form['fabric'].replace("http://", "https://")
            else:
                apic['url'] = "https://" + request.form['fabric']
            if apic['url'].endswith('/'):
                apic['url'] = apic['url'][:-1]

            apic['username'] = request.form['username']
            apic['password'] = request.form['password']
            apic['nkt_user'] = "nkt_user_" + get_random_string(6) #request.form['nkt_user']
            apic['nkt_pass'] = get_random_string(20)
            apic['private_key']= "../ansible/roles/aci/files/" + apic['nkt_user'] + '-user.key'
            apic['oob_ips'] = ""
            vc['vm_deploy'] = True if req.get("deploy_vm") == "on" else False
            # PyACI requires to have the MetaData present locally. Since the metada changes depending on the APIC version I use an init container to pull it.
            # No you can't put it in the same container as the moment you try to import pyaci it crashed is the metadata is not there. Plus init containers are cool!
            # Get the APIC Model. s.environ.get("APIC_IPS").split(',')[0] gets me the first APIC here I don't care about RR
            url = apic['url'] + '/acimeta/aci-meta.json'
            try:
                r = requests.get(url, verify=False, allow_redirects=True, timeout=5)
            except Exception as e:
                print(e)
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
    {apic['url'].replace("https://",'')}:
      validate_certs: no
      # APIC HTTPs Port
      port: 443
      # APIC user with admin credential
      admin_user: {apic['username']}
      admin_pass: {apic['password']}
      # APIC User that we create only for the duration of this playbook
      # We also create certificates for this user name to use cert based authentication
      aci_temp_username: {apic['nkt_user']}
      aci_temp_pass: {apic['nkt_pass']}"""
            with open('../ansible/inventory/apic.yaml', 'w') as f:
                f.write(config)
            # Generate temporary user and certificate
            g = proc.Group()
            g.run(["bash", "-c", "ansible-playbook -i ../ansible/inventory/apic.yaml ../ansible/apic_user.yaml --tags='apic_user'"])
            #Just wait for terraform to finish
            for s in read_process(g):
                ansible_output += str(s, 'utf-8')

            # Check the exit code of ansible playbook to create the user, if 0 all good, if not show the error.
            # This for some reason does not work on Alpine so I do a hacky thing:
            #if g.get_exit_codes()[0][1] == 0 :
            #    return redirect('/l3out')
            # If something failed then the user creation failed.
            if "failed=0" in ansible_output:
                return redirect('/l3out')
            else:
                return (Response("Unable to create the nkt user\n Ansible Output provided for debugging:\n" + ansible_output, mimetype= 'text/event-stream'))
        if fabric_type == "vxlan_evpn":
            global ndfc
            ndfc = {}
            ndfc["url"] = normalize_url(request.json["url"])
            ndfc["username"] = request.json["username"]
            ndfc["password"] = request.json["password"]
            ndfc["platform"] = "nd"  # set to nd stattically
            inst_ndfc = NDFC(ndfc["url"], ndfc["username"], ndfc["password"])
            if not inst_ndfc.logon():
                return json.dumps({"error": "login fail"}), 400
            return json.dumps({"ok": "login success"}), 200
        if button == "Previous":
            return redirect('/prereqaci')
    if request.method == "GET":
        if fabric_type == "aci":
            return render_template('login.html')
        elif fabric_type == "vxlan_evpn":
            return render_template('login_ndfc.html', fabric_type=fabric_type)


def read_process(g):
    while g.is_pending():
        lines = g.readlines()
        for prcs, line in lines:
            yield line


@app.route('/existing_cluster', methods=['GET', 'POST'])
def existing_cluster():
    fabric_type = get_fabric_type(request)
    if request.method == "POST":
        g = proc.Group()
        if fabric_type == "aci":
            g.run(["bash", "-c", "terraform destroy -auto-approve -no-color -var-file='cluster.tfvars' && \
            ansible-playbook -i ../ansible/inventory/apic.yaml ../ansible/apic_user.yaml --tags='apic_user_del'"])
        elif fabric_type == "vxlan_evpn":
            g.run(["bash",
                   "-c",
                   "terraform -chdir ndfc destroy -auto-approve -no-color -var-file='cluster.tfvars'"])
        #p = g.run("ls")
        return Response(read_process(g), mimetype='text/event-stream')
    else:

        if fabric_type == "aci":
            try:
                f = open("cluster.tfvars")
                current_config =  f.read()
                # Do something with the file
            except IOError:
                return render_template('/existing_cluster.html', text_area_title="Error", config="Config File Not Found but terraform.tfstate file is present")
            return render_template('/existing_cluster.html', text_area_title="Cluster Config:", config=current_config)
        elif fabric_type == "vxlan_evpn":
            ndfc_tfvars = "./ndfc/cluster.tfvars"
            if not os.path.exists(ndfc_tfvars):
                return render_template('/existing_cluster.html?fabric_type=vxlan_evpn',
                                       text_area_title="Error",
                                       config="Config File Not Found but terraform.tfstate file is present")
            with open(ndfc_tfvars, "r") as f:
                tf_vars = f.read()
            return render_template('/existing_cluster.html', text_area_title="Cluster Config:", config=tf_vars)


@app.route('/destroy', methods=['GET'])
def destroy():
    fabric_type = get_fabric_type(request)
    if request.method != "GET":
        return "unsupported method", 405
    g = proc.Group()
    if fabric_type == "aci":
        g.run(["bash", "-c", "terraform destroy -auto-approve -no-color -var-file='cluster.tfvars' && \
        ansible-playbook -i ../ansible/inventory/apic.yaml ../ansible/apic_user.yaml --tags='apic_user_del'"])
    elif fabric_type == "vxlan_evpn":
        g.run(["bash",
               "-c",
               "terraform -chdir=ndfc destroy -auto-approve -no-color -var-file='cluster.tfvars'"])
    #p = g.run("ls")
    return Response(read_process(g), mimetype='text/event-stream')




@app.route('/')
@app.route('/intro', methods=['GET', 'POST'])
def get_page():
    f = open("version.txt", "r")
    session['version'] = f.read()
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        fabric_type = req.get("fabric_type")
        if button == "Next":
            return redirect(f'/login?fabric_type={fabric_type}')
    if request.method == "GET":
        tf_state_aci = "terraform.tfstate"
        tf_state_ndfc = "./ndfc/terraform.tfstate"
        # if no tf state existed, return the intro page
        if not os.path.exists(tf_state_aci) and not os.path.exists(tf_state_ndfc):
            return render_template('intro.html')

        if os.path.exists(tf_state_aci):
            with open('terraform.tfstate', 'r') as f:
                state_aci = json.load(f)
            if state_aci['resources'] != []:
                return redirect('/existing_cluster')

        if os.path.exists(tf_state_ndfc):
            with open('./ndfc/terraform.tfstate', 'r') as f:
                state_ndfc = json.load(f)
                # If there are resources the cluster is there
            if state_ndfc['resources'] != []:
                return redirect('/existing_cluster?fabric_type=vxlan_evpn')
            # If the resources are not present go to intro
        return render_template('intro.html')


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        port = sys.argv[1]
    else:
        port = 5002
    app.run(host='0.0.0.0', port=port, debug=True)
