from asyncio.log import logger
import json
from logging import error
from socket import gaierror
import threading
from functools import wraps
from flask import Flask, Response, request, render_template, redirect, flash, session
from flask_executor import Executor
import vc_utils
from turbo_flask import Turbo
import requests
import os
from pyaci import Node, options, filters
import ipaddress
import re
from shelljob import proc
from packaging.version import Version
import random
import string
from datetime import datetime
import concurrent.futures
import hcl
from ndfc import NDFC, Fabric
from jinja2 import Template
import argparse
from dotenv import load_dotenv
import time
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-1s %(levelname)-1s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


VALID_FABRIC_TYPE = ['aci', 'vxlan_evpn']
TF_STATE_ACI = "terraform.tfstate"
TF_STATE_NDFC = "./ndfc/terraform.tfstate"
TEMPLATE_NAME = "nkt_template"
# app = Flask(__name__)
app = Flask(__name__, template_folder='./TEMPLATES/')
executor = Executor(app)
app.config['SECRET_KEY'] = 'cisco'
turbo = Turbo(app)

def getdotenv(env):
    '''Load dotenv'''
    try:
        load_dotenv(override=True)
        val = os.getenv(env)
        return val
    except :
        return None

def setdotenv(key, value):
    '''Set dotenv'''
    if key :
        if not value:
            value = '\'\''
        cmd = 'dotenv set ' + key + " '" + value + " '"
        os.system(cmd)
    return None

def require_api_token(func):
    '''This function is used to block direct access to all pages unless you have a session token'''
    @wraps(func)
    def check_token(*args, **kwargs):
        if 'api_session_token' not in session:
            # If it isn't return our access denied message (you can also return a redirect or render_template)
            return Response("Access denied")

        # Otherwise just send them where they wanted to go
        return func(*args, **kwargs)
    return check_token


def get_random_string(length):
    '''choose from all lowercase letter, this is used to randomize the temporary user names'''
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_fabric_type(http_request: request) -> str:
    ''' get fabric type from url parameters '''
    fabric_type = None if not http_request else http_request.args.get("fabric_type", None)
    if not fabric_type:
        fabric_type = "aci"
    return fabric_type.lower()

def normalize_url(hostname: str) -> str:
    if hostname.startswith('http://'):
        url = hostname.replace("http://", "https://")
    elif hostname.startswith("https://"):
        url = hostname
    else:
        url = "https://" + hostname
    if url.endswith('/'):
        url = url[:-1]
    return url


def normalize_apt_mirror(mirror: str) -> str:
    if mirror.startswith('http://') or mirror.startswith("https://"):
        return mirror
    else:
        return "https://" + mirror


def ndfc_process_fabric_setting(data: dict) -> bool:
    ''' NDFC: Parse the data received from the fabric page  '''

    try:
        overlay = {}
        overlay["fabric_name"] = data["fabric_name"]
        overlay["asn"] = data["asn"]
        overlay["vrf"] = data["vrf"]
        overlay["loopback_ipv4"] = data["loopback_ipv4"]
        overlay["loopback_ipv6"] = data["loopback_ipv6"]
        overlay["gateway_v4"] = data["gateway_v4"]
        overlay["gateway_v6"] = data["gateway_v6"]
        overlay["node_sub"] = data["node_sub"]
        overlay["node_sub_v6"] = data["node_sub_v6"]
        overlay["ipv6_enabled"] = data["ipv6_enabled"]
        overlay["network"] = data["network"]
        overlay["ibgp_peer_vlan"] = data["ibgp_peer_vlan"]
        overlay["bgp_pass"] = data["bgp_pass"]
        overlay["k8s_integ"] = data["k8s_integ"]
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
        
        logger.info('set overlay variable')
        setdotenv('overlay', json.dumps(overlay))
        if overlay["ipv6_enabled"]:
            setdotenv('ipv6_enabled', "")
    except KeyError as e:
        print(e)
        return False
    return True


def ndfc_create_tf_vars(fabric_type: str,
                   vc: dict,
                   ndfc: dict,
                   OVERLAY: dict,
                   calico_nodes: dict,
                   cluster: dict) -> str:
    '''Create the terraform variables for NDFC deployment'''
    with open("TEMPLATES/cluster_ndfc.tfvar.j2", "r", encoding='utf8') as f:
        tf_template = Template(f.read())
    tf_vars = tf_template.render(fabric_type=fabric_type,
                                 vc=vc,
                                 ndfc=ndfc,
                                 overlay=OVERLAY,
                                 calico_nodes=calico_nodes,
                                 cluster=cluster)
    return tf_vars


def create_l3out_vars(ipv6_enabled:bool, l3out_tenant, name, vrf, physical_dom, mtu,
                ipv4_cluster_subnet, ipv6_cluster_subnet, def_ext_epg, import_security, shared_security,
                shared_rtctrl, local_as, bgp_pass, contract, anchor_nodes):
    ''' Create the l3out variables stricture to configure ACI '''
    def_ext_epg_scope = []
    floating_ip = ""
    secondary_ip = ""
    floating_ipv6 = ""
    secondary_ipv6 = ""
    vrf_tenant = vrf_name = contract_name = contract_tenant = ""
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
    try:
        vrf_name = vrf.split('/')[1]
        vrf_tenant =  vrf.split('/')[0]
        contract_name = contract.split('/')[1]
        contract_tenant = contract.split('/')[0]
    except IndexError as e:
        print(e)
    anchor_nodes = json.loads(anchor_nodes)
    l3out = {
        "name": name,
        "l3out_tenant": l3out_tenant,
        "vrf_tenant": vrf_tenant,
        "vrf_name": vrf_name,
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
        'contract': contract_name,
        'contract_tenant': contract_tenant,
        "anchor_nodes": anchor_nodes,
        "ipv4_cluster_subnet": ipv4_cluster_subnet,
        "ipv6_cluster_subnet": ipv6_cluster_subnet,
        "ipv6_enabled": ipv6_enabled
    }
    return l3out

def create_vc_vars(url="", username="", passw="", dc="", datastore="", cluster="",
                dvs="", port_group="",
                vm_template="", vm_folder="", vm_deploy=True):

    '''Return the fomratted Virtual Center Variables'''
    vc_vars = {
        "url": url, "username": username, "pass": passw, "dc": dc, "datastore": datastore,
    "cluster": cluster, "dvs": dvs, "port_group": port_group, "vm_template": vm_template,
    "vm_folder": vm_folder, "vm_deploy": vm_deploy
    }
    return vc_vars

def create_cluster_vars(control_plane_vip="", node_sub="", node_sub_v6="", ipv4_pod_sub="", ipv6_pod_sub="", ipv4_svc_sub="", ipv6_svc_sub="", external_svc_subnet="", external_svc_subnet_v6="", local_as="", kube_version="", kubeadm_token="", 
                        crio_version="", crio_os="", haproxy_image="", keepalived_image="", keepalived_router_id="", timezone="", docker_mirror="", http_proxy_status="", http_proxy="", ntp_server="", ubuntu_apt_mirror="", sandbox_status="", eBPF_status="", dns_servers="", dns_domain=""):
                        
    ''' Generate the configuration for the Kubernetes Cluster '''
    try:
        ingress_ip = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 1)
        visibility_ip = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 2)
        neo4j_ip = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 3)
    except BaseException:
        ingress_ip = ""
        visibility_ip = ""
        neo4j_ip = ""

    #I need to have a DNS server configuired for core DNS, set one if the DNS server list is empty
    
    if dns_servers == "":
        dns_servers = ['8.8.8.8']
    else:
        dns_servers = list(dns_servers.split(","))

    ubuntu_apt_mirror = normalize_apt_mirror(ubuntu_apt_mirror)
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


@app.route('/docs/doc', methods=['GET', 'POST'])
def docs():
    '''Return the Main Documentation page '''
    if request.method == 'POST':
        return redirect('/docs/prereqaci')
    return render_template('docs/doc.html')


@app.route('/docs/prereqaci', methods=['GET', 'POST'])
def prereqaci():
    '''Return the Pre Requisites for ACI '''
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
    '''Return the NDFC Documentation '''
    return render_template('docs/ndfc.html')

@app.route('/tf_plan', methods=['GET', 'POST'])
@require_api_token
def tf_plan():
    '''Create a stream that is then fed to an iFrame to auto populate the content on the fly'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
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
@require_api_token
def tf_apply():
    '''Create a stream that is then fed to an iFrame to auto populate the content on the fly'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    g = proc.Group()
    if fabric_type == "aci":
        g.run(["bash", "-c", "terraform apply -auto-approve -no-color plan" ])
    elif fabric_type == "vxlan_evpn":
        g.run(["bash", "-c", "terraform -chdir=ndfc apply -auto-approve -no-color plan"])
    return Response( read_process(g), mimetype='text/event-stream' )

@app.route('/create', methods=['GET', 'POST'])
def create():
    '''Page that creates the cluster'''
    vkaci_ui = ""
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')

    if request.method == 'GET':
        try:
            cluster = json.loads(getdotenv('cluster'))
            vc = json.loads(getdotenv('vc'))
            calico_nodes = json.loads(getdotenv('calico_nodes'))
            if fabric_type == "aci":
                l3out = json.loads(getdotenv('l3out'))
                apic = json.loads(getdotenv('apic'))
                tf_apic = {}
                tf_apic['username'] = apic["nkt_user"]
                tf_apic['cert_name'] = apic["nkt_user"]
                tf_apic['private_key'] = apic["private_key"]
                tf_apic['url'] = apic["url"]
                tf_apic['oob_ips'] = apic["oob_ips"]
                if calico_nodes[0]['natip'] != "":
                    ext_ip = calico_nodes[0]['natip']
                else:
                    ext_ip = calico_nodes[0]['ip'].split("/")[0]
                vkaci_ui = "http://" + ext_ip + ":30000"
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

            elif fabric_type == "vxlan_evpn":
                ndfc = json.loads(getdotenv('ndfc'))
                overlay = json.loads(getdotenv('overlay'))
                config = ndfc_create_tf_vars(fabric_type,
                                        vc,
                                        ndfc,
                                        overlay,
                                        calico_nodes,
                                        cluster)
                
                with open('./ndfc/cluster.tfvars', 'w', encoding='utf-8') as f:
                    f.write(config)

            else:
                config = json.dumps({
                    "error": "fabric_type is invalid, chose between aci and vxlan_evpn"
                })
        except Exception as e:
            print(e)
            config = []
        return render_template('create.html', config=config, vkaci_ui=vkaci_ui)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Previous":
            return redirect('/cluster_network?fabric_type=' + fabric_type)
        if button == "Update Config":
            config = req.get('config')
            with open('cluster.tfvars', 'w', encoding='utf-8') as f:
                f.write(config)
            return render_template('create.html', config=config)


@app.route('/update_config', methods=['GET', 'POST'])
def update_config():
    '''Update the cluster.tfvars file'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
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
def calico_nodes_view():
    ''' Page to configure the Kubernetes nodes '''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    calico_nodes = []
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            calico_nodes = json.loads(req.get("calico_nodes"))
            logger.info('save calico_nodes variable')
            setdotenv('calico_nodes', json.dumps(calico_nodes))     
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
                l3out = json.loads(getdotenv('l3out'))
                if ipaddress.IPv4Interface(ip).ip not in ipaddress.IPv4Network(l3out["ipv4_cluster_subnet"]):
                    return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv4 must be contained in the IPv4 Cluster Subnet: " + l3out["ipv4_cluster_subnet"])
                if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(l3out["floating_ip"]).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the floating_ip " + l3out["floating_ip"])
                if ipaddress.IPv4Interface(ip).ip == ipaddress.IPv4Interface(l3out["secondary_ip"]).ip:
                    return calico_nodes_error(req.get("calico_nodes"), "The Node IP overlaps with the secondary_ip " + l3out["secondary_ip"])
            elif fabric_type == "vxlan_evpn":
                overlay = json.loads(getdotenv('overlay'))
                if ipaddress.IPv4Interface(ip).ip not in ipaddress.IPv4Network(overlay["node_sub"]):
                    return calico_nodes_error(req.get("calico_nodes"), "The Primary IPv4 must be contained in the selected Network Subnet: " + overlay["node_sub"])
            
            ipv6_enabled = getdotenv('ipv6_enabled')

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
                    l3out = json.loads(getdotenv('l3out'))
                    ip = str(ipaddress.IPv4Interface(l3out['ipv4_cluster_subnet']).ip + i) + "/" + str(ipaddress.IPv4Network(l3out["ipv4_cluster_subnet"]).prefixlen)
                elif fabric_type == "vxlan_evpn":
                    overlay = json.loads(getdotenv('overlay'))
                    host = str(ipaddress.IPv4Network(overlay['node_sub'])[i])
                    prefixlen = str(ipaddress.IPv4Network(overlay['node_sub']).prefixlen)
                    ip = f"{host}/{prefixlen}"
                ipv6 = ""
                natip = ""
                rack_id = "1"
                calico_nodes.append({"hostname": hostname, "ip": ip, "ipv6": ipv6,"natip": natip, "rack_id": rack_id})
                i += 1
        if fabric_type == "aci":
            l3out = json.loads(getdotenv('l3out'))
            return render_template('calico_nodes.html', ipv4_cluster_subnet=l3out["ipv4_cluster_subnet"], ipv6_cluster_subnet=l3out["ipv6_cluster_subnet"], calico_nodes=json.dumps(calico_nodes, indent=4))
        elif fabric_type == "vxlan_evpn":
            overlay = json.loads(getdotenv('overlay'))
            return render_template('calico_nodes.html',
                                   ipv4_cluster_subnet=overlay["node_sub"],
                                   ipv6_cluster_subnet=overlay["node_sub_v6"],
                                   calico_nodes=json.dumps(calico_nodes, indent=4))


def is_valid_hostname(hostname):
    '''Verify host name valifity'''
    if hostname == "":
        return False
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[-a-zA-Z0-9]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def calico_nodes_error(calico_nodes, error):
    ''' Handles Errors on K8S NODE PAGE calico_view'''
    if turbo.can_stream():
        return turbo.stream(
            turbo.update(render_template('_calico_nodes.html', calico_nodes=calico_nodes, error=error),
                         target='tf_calico_nodes'))


def k8s_versions():
    '''Load the list of K8s versions from the K8s_Packages'''
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
    return sorted(versions, key=Version, reverse=True)


class BetterIPv6Network(ipaddress.IPv6Network):
    '''Extend the IPv6 networks class to handle additions'''
    def __add__(self, offset):
        """Add numeric offset to the IP."""
        new_base_addr = int(self.network_address) + offset
        return self.__class__((new_base_addr, self.prefixlen))

    def size(self):
        """Return network size."""
        return 1 << (self.max_prefixlen - self.prefixlen)


class BetterIPv4Network(ipaddress.IPv4Network):
    '''Extend the IPv4 networks class to handle additions'''
    def __add__(self, offset):
        """Add numeric offset to the IP."""
        new_base_addr = int(self.network_address) + offset
        return self.__class__((new_base_addr, self.prefixlen))

    def size(self):
        """Return network size."""
        return 1 << (self.max_prefixlen - self.prefixlen)


@app.route('/cluster', methods=['GET', 'POST'])
def cluster_view():
    '''K8s Cluster view'''
    # app.logger.info(apic+apic_password+apic_username)
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            if fabric_type == "aci":
                l3out = json.loads(getdotenv('l3out'))
                ipv4_cluster_subnet = l3out['ipv4_cluster_subnet']
                ipv6_cluster_subnet = l3out['ipv6_cluster_subnet']
            elif fabric_type == "vxlan_evpn":
                overlay = json.loads(getdotenv('overlay'))
                ipv4_cluster_subnet = overlay["node_sub"]
                ipv6_cluster_subnet = overlay["node_sub_v6"]
            crio_version = req.get("kube_version").split('.')[0] + '.' + req.get("kube_version").split('.')[1]
            cluster = create_cluster_vars(req.get("control_plane_vip"), ipv4_cluster_subnet, ipv6_cluster_subnet, req.get("ipv4_pod_sub"), req.get("ipv6_pod_sub"), req.get("ipv4_svc_sub"), 
            req.get("ipv6_svc_sub"), req.get("ipv4_ext_svc_sub"), req.get("ipv6_ext_svc_sub"), req.get("local_as"),req.get("kube_version"), req.get("kubeadm_token"), crio_version, req.get("crio_os"),
            req.get("haproxy_image"), req.get("keepalived_image"), req.get("keepalived_router_id"), req.get("timezone"), req.get("docker_mirror"), req.get("http_proxy_status"), 
            req.get("http_proxy"), req.get("ntp_server"), req.get("ubuntu_apt_mirror"), req.get("sandbox_status"),req.get("eBPF_status"),req.get("dns_servers"), req.get("dns_domain"))
            logger.info('save cluster variable')
            setdotenv('cluster', json.dumps(cluster))
            if fabric_type == "aci":
                return redirect('/cluster_network')
            elif fabric_type == "vxlan_evpn":
                return redirect(f'/cluster_network?fabric_type={fabric_type}')
        elif button == "Previous":
            return redirect('/calico_nodes')
    if request.method == 'GET':
        if fabric_type == "aci":
            l3out = json.loads(getdotenv('l3out'))
            ipv4_cluster_subnet = l3out['ipv4_cluster_subnet']
        elif fabric_type == "vxlan_evpn":
            overlay = json.loads(getdotenv('overlay'))
            ipv4_cluster_subnet = overlay["node_sub"]

        api_ip = str(ipaddress.IPv4Network(ipv4_cluster_subnet, strict=False).broadcast_address - 3)

        return render_template('cluster.html', api_ip=api_ip, k8s_ver=k8s_versions())

def calculate_k8s_as(fabric_as):
    '''Ensure the K8s AS number falls within 1 and 65534'''
    fabric_as = int(fabric_as)
    if fabric_as >= 65534:
        return fabric_as -1
    return fabric_as +1

@app.route('/cluster_network', methods=['GET', 'POST'])
def cluster_network():
    '''K8s Cluster networks definition'''
    vc = json.loads(getdotenv('vc'))
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == 'POST':
        ipv6_enabled = getdotenv('ipv6_enabled')
        req = request.form
        button = req.get("button")
        if button == "Next":
            cluster = json.loads(getdotenv('cluster'))
            if not vc['vm_deploy']:
                cluster = create_cluster_vars()
                if fabric_type == "aci":
                    l3out = json.loads(getdotenv('l3out'))
                    l3out['vlan_id'] = req.get("vlan_id")
                logger.info('save cluster and l3out variables')
                setdotenv('cluster', json.dumps(cluster))
                setdotenv('l3out', json.dumps(l3out))
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
            
            logger.info('save cluster variable')
            setdotenv('cluster', json.dumps(cluster))
            return redirect(f'/create?fabric_type={fabric_type}')
        if button == "Previous" and vc['vm_deploy']:
            return redirect(f'/cluster?fabric_type={fabric_type}')
        if button == "Previous" and not vc['vm_deploy']:
            if fabric_type == "aci":
                return redirect('/l3out')
            if fabric_type == "vxlan_evpn":
                return redirect('/fabric')
    if request.method == 'GET':
        if fabric_type == "aci":
            l3out = json.loads(getdotenv('l3out'))
            ipv4_cluster_subnet = l3out['ipv4_cluster_subnet']
            k8s_local_as= calculate_k8s_as(l3out['local_as'])
        elif fabric_type == "vxlan_evpn":
            overlay = json.loads(getdotenv('overlay'))
            ipv4_cluster_subnet = overlay['node_sub']
            k8s_local_as= calculate_k8s_as(overlay["asn"])

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

        if getdotenv('ipv6_enabled'):
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
    '''vCenter Login page'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next":
            vc = create_vc_vars()
            vc["url"] = req.get("url")
            vc["username"] = req.get("username")
            vc["pass"] = req.get("pass")
            logger.info('save vc variable')
            setdotenv('vc', json.dumps(vc))
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


def update_load(ovf_handle):
    ''' Updates the progress of the upload on the UI'''
    while ovf_handle.get_upload_progress() < 99:
        time.sleep(.5)
        # x = x + 1
        htmlRendered = render_template('_template_upload_progress.html', progressVal=ovf_handle.get_upload_progress())
        # below line prints the server-side rendered html and significantly helps debugging of the progress bar
        # print(htmlRendered)
        if turbo.can_stream():
            print("Web App:" , ovf_handle.get_upload_progress())
            turbo.push(turbo.replace(htmlRendered, 'template-upload-progress'))
        else:
            print("can't stream")

@app.route('/vctemplate', methods=['GET', 'POST'])
def vctemplate():
    '''vCenter Update VM Template Page'''
    vc = json.loads(getdotenv('vc'))
    vc_folders = []
    dss = []
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Previous":
            return redirect('/vcenterlogin')
        if button == None and req.get("dc"):
            try:
                si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
            except gaierror as e:
                flash("Unable to connect to VC", 'error')
                return redirect('/vcenterlogin')
            except Exception as e:
                flash(e.msg, 'error')
                return redirect('/vcenterlogin')  

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
            try:
                si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
            except gaierror as e:
                flash("Unable to connect to VC", 'error')
                return redirect('/vcenterlogin')
            except Exception as e:
                flash(e.msg, 'error')
                return redirect('/vcenterlogin')            
            datacenter = vc_utils.get_dc(si, req.get('dc'))
            datastore = vc_utils.get_ds(datacenter, req.get('datastore'))
            resource_pool = vc_utils.get_largest_free_rp(si, datacenter)
            ova_path = str(os.getcwd()) + "/static/vm_templates/" + TEMPLATE_NAME + ".ova"
            ovf_handle = vc_utils.OvfHandler(ova_path)
            ovf_manager = si.content.ovfManager
            cisp = vc_utils.import_spec_params(entityName=TEMPLATE_NAME, diskProvisioning='thin')

            cisr = ovf_manager.CreateImportSpec(ovf_handle.get_descriptor(), resource_pool, datastore, cisp)
            if cisr.error:
                print("The following errors will prevent import of this OVA:")
                for error in cisr.error:
                    print("%s" % error)

            ovf_handle.set_spec(cisr)

            # Run the update_load function in a new thread
            executor.submit(update_load, ovf_handle)

            #Start upload as a new thread
            #Find Folder
            # Get only 1st level folder
            for child in datacenter.vmFolder.childEntity:
                if vc_utils.find_folders(child):
                    if child.name == req.get('vm_folder'):
                        folder = child

            # If the template already exists, delete it!
            vm = vc_utils.find_by_name(si,folder,TEMPLATE_NAME)
            if vm:
                task = vm.Destroy_Task()
                vc_utils.wait_for_tasks(si, [task])
            upload = concurrent.futures.ThreadPoolExecutor()
            upload.submit(vc_utils.start_upload, vc["url"], resource_pool,cisr, folder, ovf_handle)
            # Wait for upload to complete UI freeze here
            upload.shutdown(wait=True)
            vm = vc_utils.find_by_name(si,folder,TEMPLATE_NAME)
            vm.CreateSnapshot_Task(name=str(datetime.now()),
                                        description="Snapshot",
                                        memory=False,
                                        quiesce=False)

            # Add Note to VM:
            spec = vc_utils.vim.vm.ConfigSpec()
            spec.annotation = TEMPLATE_NAME
            vm.ReconfigVM_Task(spec)

            return redirect('/vcenter')

    if request.method == 'GET':
        try:
            si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
        except gaierror as e:
            flash("Unable to connect to VC", 'error')
            return redirect('/vcenterlogin')
        except Exception as e:
            flash(e.msg, 'error')
            return redirect('/vcenterlogin')

        dcs = vc_utils.get_all_dcs(si)
        vc_utils.disconnect(si)
        return render_template('vc_template_upload.html', dcs=dcs.values(), progressVal=0)
        # return turbo.stream(
        #     turbo.update(render_template('vc_template_upload.html', dcs=dcs.values(), progressVal=0),
        #                  target='vc_template_upload'))

@app.route('/vcenter', methods=['GET', 'POST'])
def vcenter():
    '''vCenter Maing Page'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    dvss = []
    vm_templates = []
    vc_folders = []
    pgs = []
    clusters = []
    if request.method == 'POST':
        vc = json.loads(getdotenv('vc'))
        req = request.form
        button = req.get("button")
        if button == "Next":
            vm_templates_and_ds = json.loads(getdotenv('vm_templates_and_ds'))
            vc["vm_template"] = req.get('vm_templates')
            vc["vm_folder"] = req.get('vm_folder')
            vc["dc"] = req.get('dc')
            vc["datastore"] =vm_templates_and_ds[vc["vm_template"]][0]
            vc["cluster"] = req.get('cluster')
            vc["dvs"] = req.get('port_group').split('/')[0]
            vc["port_group"] = req.get('port_group').split('/')[1]
            if fabric_type == "aci":
                l3out = json.loads(getdotenv('l3out'))
                l3out['vlan_id'] = req.get('port_group').split('/')[2].split('-')[1]
                logger.info('save l3out, variable')
                setdotenv('l3out', json.dumps(l3out))
            logger.info('save vc, variable')
            setdotenv('vc', json.dumps(vc))
            if fabric_type == "vxlan_evpn":
                return redirect(f'/calico_nodes?fabric_type={fabric_type}')
            else:
                return redirect('/calico_nodes')
        elif button == "Previous":
            return redirect(f'/vcenterlogin?fabric_type={fabric_type}')

        elif button == None and req.get("dc"):
            try:
                si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
            except gaierror as e:
                flash("Unable to connect to VC", 'error')
                return redirect('/vcenterlogin')
            except Exception as e:
                flash(e.msg, 'error')
                return redirect('/vcenterlogin')                     
            dcs = vc_utils.get_all_dcs(si)
            dc_name = req.get('dc')
            for dc in dcs:
                if dc.name == dc_name:
                    vc_utils.find_vms(dc, vm_templates, TEMPLATE_NAME)
                    #once I found the VMs I made a dic of VM to Datastore so I can get the DS directly
                    vm_templates_and_ds = {}
                    for vm in vm_templates:
                        dsl = []
                        for ds in vm.datastore:
                            dsl.append(ds.info.name)
                        vm_templates_and_ds[vm.name] = dsl
                    vc_utils.find_pgs(dc, pgs)
                    for child in dc.hostFolder.childEntity:
                        if (vc_utils.find_compute_cluster(child)):
                            clusters.append(child.name)
                    # Get only 1st level folder
                    for child in dc.vmFolder.childEntity:
                        if vc_utils.find_folders(child):
                            vc_folders.append(child.name)
            vc_folders = sorted(vc_folders, key=str.lower)
            #dss = sorted(dss, key=str.lower)
            dvss = sorted(dvss, key=str.lower)
            vm_templates_names = sorted([o.name for o in vm_templates], key=str.lower)
            vc_folders = sorted(vc_folders, key=str.lower)
            pgs = sorted(pgs, key=str.lower)
            clusters = sorted(clusters, key=str.lower)
            vc_utils.disconnect(si)
            logger.info('save vm_templates_and_ds variable')
            setdotenv('vm_templates_and_ds', json.dumps(vm_templates_and_ds))
            if turbo.can_stream():
                return turbo.stream(
                    turbo.replace(render_template('_vc_details.html', clusters=clusters, vm_templates=vm_templates_names, vc_folders=vc_folders, pgs=pgs),
                                  target='vc'))

    if request.method == 'GET':
        vc = json.loads(getdotenv('vc'))
        try:
            si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
        except gaierror as e:
            flash("Unable to connect to VC", 'error')
            return redirect('/vcenterlogin')
        except Exception as e:
            flash(e.msg, 'error')
            return redirect('/vcenterlogin')

        dcs = vc_utils.get_all_dcs(si)
        vc_utils.disconnect(si)
        return render_template('vcenter.html', dcs=dcs.values(), fabric_type=fabric_type)


def anchor_node_error(anchor_nodes, pod_ids, nodes_id, rtr_id, error):
    '''Handle Anchor node Errors'''
    if turbo.can_stream():
        return turbo.stream(
            turbo.update(render_template('_anchor_nodes.html', pod_ids=pod_ids, nodes_id=nodes_id, anchor_nodes=anchor_nodes, rtr_id=rtr_id, error=error),
                         target='anchor_nodes'))


@app.route('/l3out', methods=['GET', 'POST'])
def l3out_view():
    ''' l3out page view '''
    apic = json.loads(getdotenv('apic'))
    phys_dom = []
    tenants = []
    vrfs = ["Select a Tenant"]
    local_as = ""
    anchor_nodes = []
    home = os.path.expanduser("~")
    meta_path = home + '/.aci-meta/aci-meta.json'
    pyaci_apic = Node(apic['url'], aciMetaFilePath=meta_path)
    rtr_id_counter = ipaddress.IPv4Address("1.1.1.1")
    try:
        pyaci_apic.useX509CertAuth(apic['nkt_user'],apic["nkt_user"],apic['private_key'])
    except FileNotFoundError as e:
        print(e)
        return redirect('/login')
    if request.method == 'POST':
        vc = json.loads(getdotenv('vc'))
        ipv6_enabled = True if getdotenv('ipv6_enabled') else False
        req = request.form
        button = req.get("button")
        if button == "Next":
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

            l3out = create_l3out_vars(ipv6_enabled, req.get("l3out_tenant"), req.get("name"), req.get("vrf_name"), req.get("physical_dom"), req.get("mtu"), req.get("ipv4_cluster_subnet"), req.get("ipv6_cluster_subnet"), req.get("def_ext_epg"), req.get(
                "import-security"), req.get("shared-security"), req.get("shared-rtctrl"), req.get("local_as"), req.get("bgp_pass"), req.get("contract"), req.get("anchor_nodes"))
            logger.info('save l3out variable')
            setdotenv('l3out', json.dumps(l3out))
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

            vzBrCPs = pyaci_apic.methods.ResolveClass('vzBrCP').GET(
                **options.filter(filters.Wcard('fvCtx.dn', regex)))
            for vzBrCP in vzBrCPs:
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
                logger.info('save ipv6_enabled variable')
                ipv6_enabled = True
                setdotenv('ipv6_enabled', "")
            
            rack_id = req.get("rack_id")
            rtr_id = req.get("rtr_id")
            primary_ip = req.get("node_ipv4")

            # I check here also the other parameters

            try:
                # Use the Netwrok to ensure that the mask is always present
                if ipaddress.IPv4Network(
                    req.get("ipv4_cluster_subnet"), strict=True).prefixlen == 32:
                    raise ValueError("Please Specify a Prefix Len in /XX format")

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

        # Set APIC OOB to an empty list, so if we refresh the page we do not keep appending the same IPs
        apic['oob_ips'] = ""
        for a in apics:
            apic['oob_ips'] += (a.oobMgmtAddr) + ","
        #Remove the last comma
        apic['oob_ips'] = apic['oob_ips'][:-1]
        phys_dom = sorted(phys_dom, key=str.lower)
        tenants = sorted(tenants, key=str.lower)
        session['nodes_id'] = sorted(nodes_id, key=int)
        session['pod_ids'] = sorted(pod_ids, key=int)
        logger.info('save apic variable')
        setdotenv('apic', json.dumps(apic))
        return render_template('l3out.html', phys_dom=phys_dom, tenants=tenants, vrfs=vrfs, local_as=local_as, pod_ids=session['pod_ids'], nodes_id=session['nodes_id'], rtr_id=str(rtr_id_counter))

@app.route("/fabric", methods=["GET", "POST"])
def fabric():
    '''Fabric page, will load the ACI or NDFC page depening on the fabric_type in the URL'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if not getdotenv("ndfc"):
        return redirect(f"/login?fabric_type={fabric_type}")
    if request.method == "GET":
        if fabric_type == "vxlan_evpn":
            fabrics = []
            ndfc = json.loads(getdotenv('ndfc'))
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
        result = ndfc_process_fabric_setting(data)
        if result:
            return json.dumps({"ok": "fabric setting configured"}), 200
        else:
            return json.dumps({"error": "invalid settings"}), 400


@app.route("/query_ndfc", methods=["GET"])
def query_ndfc():
    '''function to implement query ndfc API'''
    fabric_name = request.args.get("fabric_name")
    query_vrf = request.args.get("query_vrf")
    query_net = request.args.get("query_network")
    query_inv = request.args.get("query_inv")
    vrf_name = request.args.get("vrf_name")
    logger.info('fabric page: load env variables')
    ndfc = json.loads(getdotenv('ndfc'))
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
    '''Login page to get details for ACI or NDFC'''
    apic = {}
    vc = create_vc_vars()
    ansible_output = ''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Login":
            apic['url'] = normalize_url(request.form['fabric'])
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
            logger.info('login page: set apic variables')
            setdotenv('apic', json.dumps(apic))
            logger.info('login page: set vc variables')
            setdotenv('vc', json.dumps(vc))
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
            ndfc = {}
            ndfc["url"] = normalize_url(request.json["url"])
            ndfc["username"] = request.json["username"]
            ndfc["password"] = request.json["password"]
            ndfc["platform"] = "nd"  # set to nd stattically
            inst_ndfc = NDFC(ndfc["url"], ndfc["username"], ndfc["password"])
            if not inst_ndfc.logon():
                return json.dumps({"error": "login fail"}), 400
            logger.info('login page: set ndfc variable')
            setdotenv('ndfc', json.dumps(ndfc))
            return json.dumps({"ok": "login success"}), 200
        if button == "Previous":
            return redirect('/prereqaci')
    if request.method == "GET":

        #I wanna have an clean environment so if .env exists I epty it
        if os.path.exists('.env'):
            with open('.env', 'w'):
                logger.info('Cleared .env file')

        if fabric_type == "aci":
            return render_template('login.html')
        elif fabric_type == "vxlan_evpn":
            return render_template('login_ndfc.html', fabric_type=fabric_type)


def read_process(g):
    '''Read output from the background proccess that is running terraform and ansible'''
    while g.is_pending():
        lines = g.readlines()
        for prcs, line in lines:
            yield line


@app.route('/reset', methods=['GET'])
@require_api_token
def reset():
    '''generic function to delete the TF State'''
    fabric_type = get_fabric_type(request)

    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == "GET":
        try:
            if fabric_type == "aci":
                if os.path.exists(TF_STATE_ACI):
                    os.remove(TF_STATE_ACI)
                    return Response("Deleted terraform state file " + TF_STATE_ACI)
                else:
                    return Response("terraform state file " + TF_STATE_ACI +" Not found")
            if fabric_type == "vxlan_evpn":
                if os.path.exists(TF_STATE_NDFC):
                    os.remove(TF_STATE_NDFC)
                    return Response("Deleted terraform state file " + TF_STATE_NDFC)
                else:
                    return Response("terraform state file " + TF_STATE_NDFC +" Not found")
        except Exception:
           return Response("Reset Failed")

@app.route('/existing_cluster', methods=['GET'])
@require_api_token
def existing_cluster():
    '''Page that detects an existing cluster and allow the user to destroy it'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if fabric_type == "aci":
        try:
            f = open("cluster.tfvars")
            current_config =  f.read()
            # Derive vkaci IP address:
            master = hcl.loads(current_config)['calico_nodes'][0]
            if master['natip'] != "":
                ext_ip = master['natip']
            else:
                ext_ip = master['ip'].split("/")[0]

            vkaci_ui = "http://" + ext_ip + ":30000"
            # Do something with the file
        except IOError:
            return render_template('/existing_cluster.html', text_area_title="Error", config="Config File Not Found but terraform.tfstate file is present")
        return render_template('/existing_cluster.html', text_area_title="Cluster Config:", config=current_config, vkaci_ui=vkaci_ui)
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
@require_api_token
def destroy():
    '''Destroy the ACI/NDFC Config and VM'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method != "GET":
        return "unsupported method", 405
    g = proc.Group()
    if fabric_type == "aci":
        g.run(["bash", "-c", "terraform destroy -auto-approve -no-color -var-file='cluster.tfvars' && \
        ansible-playbook -i ../ansible/inventory/apic.yaml ../ansible/apic_user.yaml --tags='apic_user_del'"])
    elif fabric_type == "vxlan_evpn":
        integ_reset = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -i ../ansible/inventory/ndfc.yaml ../ansible/ndfc_integration.yaml -t reset"
        tf_destory = "terraform -chdir=ndfc destroy -auto-approve -no-color -var-file='cluster.tfvars'"
        if os.path.exists("../ansible/inventory/ndfc.yaml"):
            cmd = f"{integ_reset} && {tf_destory}"
        else:
            cmd = tf_destory
        g.run(["bash", "-c", cmd])
    #p = g.run("ls")
    return Response(read_process(g), mimetype='text/event-stream')




@app.route('/')
@app.route('/intro', methods=['GET', 'POST'])
def get_page():
    '''Intro page'''
    session['api_session_token'] = get_random_string(50)
    f = open("version.txt", "r", encoding='utf-8')
    session['version'] = f.read()
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        fabric_type = req.get("fabric_type")
        if fabric_type not in VALID_FABRIC_TYPE:
            return redirect('/')
        if button == "Next":
            return redirect(f'/login?fabric_type={fabric_type}')
    if request.method == "GET":
        # if no tf state existed, return the intro page
        if not os.path.exists(TF_STATE_ACI) and not os.path.exists(TF_STATE_NDFC):
            return render_template('intro.html')

        if os.path.exists(TF_STATE_ACI):
            with open('terraform.tfstate', 'r', encoding='utf-8') as f:
                state_aci = json.load(f)
            if state_aci['resources'] != []:
                return redirect('/existing_cluster')

        if os.path.exists(TF_STATE_NDFC):
            with open('./ndfc/terraform.tfstate', 'r', encoding='utf-8') as f:
                state_ndfc = json.load(f)
                # If there are resources the cluster is there
            if state_ndfc['resources'] != []:
                return redirect('/existing_cluster?fabric_type=vxlan_evpn')
            # If the resources are not present go to intro
        return render_template('intro.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Nexus Kubernetes Tool allows you to configure your ACI/NDFC fabric and bootstrap a Kubernetes Cluster')
    parser.add_argument('-p', dest='port', type=int, default=80, help='The TCP port the webserver listens to')
    parser.add_argument('-d', dest='debug', action='store_true', default=False, help='Run Flask in debug mode')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=args.debug)
