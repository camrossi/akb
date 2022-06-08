import json
import requests
from OpenSSL.crypto import sign, load_privatekey, FILETYPE_PEM
import base64
from socket import gaierror
from functools import wraps
from flask import Flask, Response, request, render_template, redirect, flash, session, escape
from flask_executor import Executor
import vc_utils
from turbo_flask import Turbo
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
import hcl2
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
TF_LOCK = ".terraform.tfstate.lock.info"
ANSIBLE_LOCK = ".ansible.lock.info"
ANSIBLE_LOCK_CMD = "touch " + ANSIBLE_LOCK
ANSIBLE_UNLOCK_CMD = "rm " + ANSIBLE_LOCK
TEMPLATE_NAME = "nkt_template"
# app = Flask(__name__)
app = Flask(__name__, template_folder='./TEMPLATES/')
app.config['SECRET_KEY'] = 'cisco'
executor = Executor(app)
turbo = Turbo(app)

def getdotenv(env):
    '''Load dotenv'''
    try:
        load_dotenv(override=True)
        val = os.getenv(env)
        logger.debug('getdotenv %s %s', env, val)
        return val
    except :
        logger.error('getdotenv failed to load %s', env)
        return None

def unsetdotenv(key):
    '''UnSet dotenv'''
    cmd = 'dotenv unset ' + key
    os.system(cmd)
    return None
def getdotenvjson(env):
    '''Load dotenv as json'''
    try:
        val = getdotenv(env)
        return json.loads(val)
    except:
        return None

def setdotenv(key, value):
    '''Set dotenv'''
    if key :
        if not value:
            value = '\'\''
        cmd = 'dotenv set ' + key + " '" + value + " '"
        os.system(cmd)
    return None
def update_all_dotenv(config):
    logger.info('update_all_dotenv')
    config = hcl2.loads(config)
    if 'apic' in config:
        # If the admin user is already present, save it.
        existing_apic = json.loads(getdotenv('apic'))
        if 'adminuser' in existing_apic and 'adminpass' in existing_apic and \
        'adminuser' not in config['apic'] and 'adminpass' not in config['apic']:
            logger.info('Detected per-existing APIC user and no new admin user credentials passed')
            config['apic']['adminuser'] = existing_apic['adminuser']
            config['apic']['adminpass'] = existing_apic['adminpass']
        setdotenv('apic', json.dumps(config['apic']))

    if 'calico_nodes' in config:
        setdotenv('calico_nodes', json.dumps(config['calico_nodes']))
    if 'k8s_cluster' in config:
        setdotenv('cluster', json.dumps(config['k8s_cluster']))
    if 'l3out' in config:
        setdotenv('l3out', json.dumps(config['l3out']))
    if 'vc' in config:
        setdotenv('vc', json.dumps(config['vc']))
    if 'ndfc' in config:
        setdotenv('ndfc', json.dumps(config['ndfc']))
    if 'overlay' in config:
        setdotenv('overlay', json.dumps(config['overlay']))

def deldotenv(key):
    '''Del dotenv'''
    cmd = 'dotenv unset ' + key
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


def get_random_string(length, password = False):
    '''choose from all lowercase letter, this is used to randomize the temporary user names'''
    letters = string.ascii_letters + string.digits
    # I just add a ! as special char as using string.punctuation introduces also char that are not accepted by APIC or create issues with Ansible
    result_str = ''.join(random.choice(letters) for i in range(length)) 
    if password:
        result_str = result_str + "!Aa1"
    return result_str


def get_fabric_type(http_request: request) -> str:
    ''' get fabric type from url parameters '''
    fabric_type = None if not http_request else http_request.args.get("fabric_type", None)
    if not fabric_type:
        fabric_type = "aci"
    return fabric_type.lower()

def get_manage_cluster(http_request: request) -> bool:
    ''' get manage cluster from url parameters '''
    manage_cluster = 'False' if not http_request else http_request.args.get("manage", 'False')
    manage_cluster = str(manage_cluster).lower()
    if manage_cluster == "true":
        return True
    return False

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
    if mirror == "":
        return mirror
    if mirror.startswith('http://') or mirror.startswith("https://"):
        return mirror
    else:
        return "https://" + mirror


def validate_fabric_input(data: dict) -> (bool, str):
    print(data)
    inval_key = []
    for key, value in data.items():
        if value:
            continue
        # none mandatory keys
        if key in ["k8s_integ", "bgp_pass", "ipv6_enabled"]:
            continue
        # none mandatory ipv6 keys if ipv6 is not enabled
        if key in ["loopback_ipv6", "node_sub_v6", "gateway_v6"] and not data["ipv6_enabled"]:
            continue
        inval_key.append(key)
    if inval_key != []:
        return False, f"Invalid keys: {inval_key}"
    else:
        return True, "valid input!"


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
        else:
            unsetdotenv('ipv6_enabled')
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
                        crio_version="", crio_os="", haproxy_image="", keepalived_image="", keepalived_router_id="", timezone="", docker_mirror="", http_proxy_status="", http_proxy="", ntp_server="", ubuntu_apt_mirror="", sandbox_status="", eBPF_status="", dns_servers="", dns_domain="", cni_plugin=""):
                        
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
                "vip_port": control_plane_vip.split(":")[1] if control_plane_vip != "" else 0,
                "pod_subnet": ipv4_pod_sub, 
                "pod_subnet_v6": ipv6_pod_sub,
                "cluster_svc_subnet": ipv4_svc_sub,
                "cluster_svc_subnet_v6": ipv6_svc_sub,
                "external_svc_subnet": external_svc_subnet,
                "external_svc_subnet_v6": external_svc_subnet_v6,
                "local_as" : local_as if local_as != "" else 0,
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
                "dns_servers" : dns_servers,
                "cni_plugin": cni_plugin
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

@app.route('/tf_running', methods=['GET', 'POST'])
def tf_running():
    if os.path.exists(TF_LOCK) or os.path.exists("./ndfc/" + TF_LOCK):
        return Response( 'True', mimetype='text/plain')
    return Response( 'False', mimetype='text/plain')

@app.route('/ansible_running', methods=['GET', 'POST'])
def ansible_running():
    if os.path.exists(ANSIBLE_LOCK):
        return Response( 'True', mimetype='text/plain')
    return Response( 'False', mimetype='text/plain')

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
    config_file = "cluster.tfvars"
    if fabric_type == "vxlan_evpn":
        config_file = "ndfc/" + config_file 
    with open(config_file, 'r') as fp:
        current_config = hcl2.load(fp)
        print(current_config)
    if not current_config['vc']['vm_deploy']:
        logger.info('K8s Cluster deployment disabled')
        #Change to the VM module directory
        os.chdir("modules/k8s_node")
        if os.path.exists("vms.tf"):
            logger.info('Disable VM Deployment')
            os.rename("vms.tf","vms.tf.ignore")
        if os.path.exists("outputs.tf"):
            logger.info('Enable Config Only outputs')
            os.rename("outputs.tf","outputs.tf.ignore")
            os.rename("outputs_novms.tf.ignore","outputs_novms.tf")
        if os.path.exists("group_var_template.tmpl"):
            logger.info('Enable Config Only Templates')
            os.rename("group_var_template.tmpl","group_var_template.tmpl.ignore")
            os.rename("group_var_template_novms.tmpl.ignore","group_var_template_novms.tmpl")
        os.chdir(cwd)
    if current_config['vc']['vm_deploy']:
        logger.info('K8s Cluster enbaled, enable vms and output tf files')
        os.chdir("modules/k8s_node")
        if os.path.exists("vms.tf.ignore"):
            logger.info('Enable VM Deployment')
            os.rename("vms.tf.ignore","vms.tf")
        if os.path.exists("outputs.tf.ignore"):
            logger.info('Enable Cluster Deployment outputs')
            os.rename("outputs.tf.ignore","outputs.tf")
            os.rename("outputs_novms.tf","outputs_novms.tf.ignore")
        if os.path.exists("group_var_template.tmpl.ignore"):
            logger.info('Enable Cluster Templates')
            os.rename("group_var_template.tmpl.ignore","group_var_template.tmpl")
            os.rename("group_var_template_novms.tmpl","group_var_template_novms.tmpl.ignore")
        os.chdir(cwd)
    if fabric_type == "aci":
        apic = json.loads(getdotenv('apic'))
        ret = create_apic_user(apic)
        if ret != 'OK':
            return ret
        if not os.path.exists('.terraform'):     
            g.run(["bash", "-c", "terraform init -no-color && terraform plan -no-color -var-file='cluster.tfvars' -out='plan'" ])
        else:
            g.run(["bash", "-c", "terraform plan -no-color -var-file='cluster.tfvars' -out='plan'"])
    elif fabric_type == "vxlan_evpn":
        if not os.path.exists('ndfc/.terraform'):
            g.run(["bash", "-c", "terraform -chdir=ndfc init -no-color && terraform -chdir=ndfc plan -no-color -var-file='cluster.tfvars' -out='plan'"])
        else:
            g.run(["bash", "-c", "terraform -chdir=ndfc plan -no-color -var-file='cluster.tfvars' -out='plan'"])
    return Response(read_process(g), mimetype='text/event-stream')

def node_delta(chdir):
    '''Calculte the new and removed k8s nodes'''
    cmd = "terraform -chdir="+chdir+" show -json plan"
    stream = os.popen(cmd)
    new_nodes = set()
    removed_nodes = set()
    changes = json.loads(stream.read())
    for change in changes['resource_changes']:
        if "module.k8s_node.vsphere_virtual_machine.vm" in change['address']:
            if "create" in change['change']['actions']:
                new_nodes.add(change['index'])
            if "delete" in change['change']['actions']:
                removed_nodes.add(change['index'])
    return new_nodes, removed_nodes

@app.route('/tf_apply', methods=['GET', 'POST'])
@require_api_token
def tf_apply():
    '''Create a stream that is then fed to an iFrame to auto populate the content on the fly'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if fabric_type == "aci":
        chdir ="."
    elif fabric_type == "vxlan_evpn":
        chdir ="ndfc"
    plan = chdir + "/plan"
    if not os.path.exists(plan):
        return Response('Please run "Plan" before "Apply"')
    g = proc.Group()
    cluster_status = check_if_new_cluster()
    if cluster_status == 'new':
        logger.info("Deploy")
        g.run(["bash", "-c","terraform -chdir="+chdir+" apply -auto-approve -no-color plan"])
    else:
        new_nodes, removed_nodes = node_delta(chdir)
        rm_cmd = ""
        add_cmd = ""
        plan_cmd = ""
        if len(removed_nodes) > 0:
            limit = ','.join(str(s) for s in removed_nodes)
            logger.info("Removing Nodes %s", limit)
            rm_cmd="ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook \
                -i ../ansible/inventory/nodes.ini ../ansible/remove_k8s_nodes.yaml --limit='"+ limit+"' &&\
                terraform -chdir="+chdir+" apply -auto-approve -no-color plan"
        if len(new_nodes) > 0:
            limit = ','.join(str(s) for s in new_nodes)
            logger.info("Adding Nodes %s", limit)
            # I need to update labes etc... so I need to pass the primary master as well
            primary_master = json.loads(getdotenv('calico_nodes'))[0]['hostname']
            new_nodes.add(primary_master)
            
            limit = ','.join(str(s) for s in new_nodes)
            add_cmd="terraform -chdir="+chdir+" apply -auto-approve -no-color plan && \
                    ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b \
                    -i ../ansible/inventory/nodes.ini ../ansible/add_nodes.yaml \
                    --limit='"+ limit+"'"
        # If I am adding and removing I need to plan again in the middle
        if len(new_nodes) > 0 and len(removed_nodes) > 0:
            plan_cmd = "terraform -chdir="+chdir+" plan -no-color -var-file='cluster.tfvars' -out='plan'"
        '''I don't particularly like runing all this with && but shellgob.Proc schedule the tasks in 
           parallel so it ends up running add and remove in parallel and bricks the cluster, need to evaluate changing
           to a diffrent library perhaps 
        '''
        cmds = [ANSIBLE_LOCK_CMD, rm_cmd, plan_cmd, add_cmd, ANSIBLE_UNLOCK_CMD]
        g.run(["bash", "-c", ';'.join(filter(None, cmds))])


    return Response( read_process(g), mimetype='text/event-stream' )

def create_tf_config(fabric_type):
    ''' Puts all the config pieces togehter and generate the TF config'''
    vkaci_ui = ""
    try: 
        try:
            vc = json.loads(getdotenv('vc'))
        except Exception as e:
            vc = {}
            vc['vm_deploy'] = True
        cluster = json.loads(getdotenv('cluster'))
        if fabric_type == "aci":
            l3out = json.loads(getdotenv('l3out'))
            apic = json.loads(getdotenv('apic'))
            tf_apic = {}
            tf_apic['nkt_user'] = apic["nkt_user"]
            tf_apic['cert_name'] = apic["nkt_user"]
            tf_apic['private_key'] = apic["private_key"]
            tf_apic['url'] = apic["url"]
            tf_apic['oob_ips'] = apic["oob_ips"]
            ext_ip = ""
            if vc['vm_deploy']:
                calico_nodes = json.loads(getdotenv('calico_nodes'))
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
            if vc['vm_deploy']:
                calico_nodes = json.loads(getdotenv('calico_nodes'))
            else:
                calico_nodes = ""
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
    return config, vkaci_ui, vc['vm_deploy']

@app.route('/create', methods=['GET', 'POST'])
def create():
    '''Page that creates the cluster'''
    vkaci_ui = ""
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == 'GET':
        config, vkaci_ui, vm_deploy = create_tf_config(fabric_type)
        return render_template('create.html', fabric_type=fabric_type, config=config, vkaci_ui=vkaci_ui, vm_deploy=vm_deploy)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Previous":
            return redirect('/cluster_network?fabric_type=' + fabric_type)

@app.route('/update_config', methods=['GET', 'POST'])
def update_config():
    '''Update the cluster.tfvars file'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == "POST":
        if fabric_type == "aci":
            config = request.json.get("config", "[]")
            update_all_dotenv(config)
            with open('cluster.tfvars', 'w') as f:
                f.write(config)
            return json.dumps({"msg": "Config update success!"}), 200
        elif fabric_type == "vxlan_evpn":
            config = request.json.get("config", "[]")
            update_all_dotenv(config)
            with open('./ndfc/cluster.tfvars', 'w') as f:
                f.write(config)
            return json.dumps({"msg": "Config update success!"}), 200
        else:
            return json.dumps({"error": "invalid fabric type"}), 400


@app.route('/calico_nodes', methods=['GET', 'POST'])
def calico_nodes_view():
    ''' Page to configure the Kubernetes nodes '''
    fabric_type = get_fabric_type(request)
    manage_cluster = get_manage_cluster(request)
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
            return redirect(f'/vcenter?fabric_type={fabric_type}')
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
                return calico_nodes_error(json.dumps(calico_nodes, indent=4), "Error: Invalid Hostname")

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
                    return calico_nodes_error(req.get("calico_nodes"), "Duplicated Hostname " + hostname)
                if calico_node['ip'] == ip:
                    return calico_nodes_error(req.get("calico_nodes"), "Duplicated Node IPv4: " + ip)
                if ipv6_enabled:
                    if calico_node['ipv6'] == ipv6:
                        return calico_nodes_error(req.get("calico_nodes"), "Duplicated Node IPv6: " + ipv6)

            calico_nodes.append({"hostname": hostname, "ip": ip,
                                "ipv6": ipv6, "natip": natip, "rack_id": rack_id})
            return stream_calico_nodes_update(calico_nodes)

        if button == "Remove Node":
            hostname = req.get("hostname")
            calico_nodes = json.loads(req.get("calico_nodes"))
            if hostname in list(d['hostname'] for d in calico_nodes[0:3]):
                return calico_nodes_error(req.get("calico_nodes"), "Cannot Remove Master Nodes")
            
            for node in calico_nodes:
                if hostname == node['hostname']:
                    calico_nodes.remove(node)
            return stream_calico_nodes_update(calico_nodes)

            return calico_nodes_error(calico_nodes, "Error: Hostname not found")
        if button == "Apply Node Config Update":
            #Update the calico node env virable with the new config
            calico_nodes = json.loads(req.get("calico_nodes"))
            logger.info('save calico_nodes variable')
            setdotenv('calico_nodes', json.dumps(calico_nodes))
            create_tf_config(fabric_type)
            return redirect(f"/create?fabric_type={fabric_type}")

    if request.method == 'GET':
        # Try to load the calico nodes from the env file.
        #If it fails assume is empty and move on to pre-populate
        try:
            calico_nodes = json.loads(getdotenv('calico_nodes'))
        except TypeError:
            pass
        if calico_nodes == []:
            ipv6_enabled = getdotenv('ipv6_enabled')
            print("ipv6_enabled: ", ipv6_enabled)
            i = 1
            while i <= 3:
                hostname = 'nkt-master-' + str(i)
                ipv6 = ""
                natip = ""
                rack_id = "1"
                if fabric_type == "aci":
                    l3out = json.loads(getdotenv('l3out'))
                    ip = str(ipaddress.IPv4Interface(l3out['ipv4_cluster_subnet']).ip + i) + "/" + str(ipaddress.IPv4Network(l3out["ipv4_cluster_subnet"]).prefixlen)
                    if ipv6_enabled:
                        ipv6 = str(ipaddress.IPv6Interface(l3out['ipv6_cluster_subnet']).ip + i) + "/" + str(ipaddress.IPv6Network(l3out["ipv6_cluster_subnet"]).prefixlen)
                elif fabric_type == "vxlan_evpn":
                    overlay = json.loads(getdotenv('overlay'))
                    host = str(ipaddress.IPv4Network(overlay['node_sub'])[i])
                    prefixlen = str(ipaddress.IPv4Network(overlay['node_sub']).prefixlen)
                    ip = f"{host}/{prefixlen}"
                    if ipv6_enabled:
                        ipv6 = str(ipaddress.IPv6Interface(overlay['node_sub_v6']).ip + i) + "/" + str(ipaddress.IPv6Network(overlay["node_sub_v6"]).prefixlen)

                calico_nodes.append({"hostname": hostname, "ip": ip, "ipv6": ipv6,"natip": natip, "rack_id": rack_id})
                i += 1
        ipv4_cluster_subnet = None
        ipv6_cluster_subnet = None
        if fabric_type == "aci":
            l3out = json.loads(getdotenv('l3out'))
            ipv4_cluster_subnet=l3out["ipv4_cluster_subnet"]
            ipv6_cluster_subnet=l3out["ipv6_cluster_subnet"]
        elif fabric_type == "vxlan_evpn":
            overlay = json.loads(getdotenv('overlay'))
            ipv4_cluster_subnet=overlay["node_sub"]
            ipv6_cluster_subnet=overlay["node_sub_v6"]
        return render_template('calico_nodes.html',
                                ipv4_cluster_subnet=ipv4_cluster_subnet,
                                ipv6_cluster_subnet=ipv6_cluster_subnet,
                                calico_nodes=json.dumps(calico_nodes, indent=4),
                                hostnames = get_hostnames(calico_nodes),
                                manage_cluster=manage_cluster,
                                fabric_type=fabric_type)


def stream_calico_nodes_update(calico_nodes):
    if turbo.can_stream():
        return turbo.stream([
            turbo.update(render_template('_calico_nodes.html', calico_nodes=json.dumps(calico_nodes, indent=4)),
                        target='tf_calico_nodes'),
            turbo.update(render_template('_calico_hostnames.html', hostnames=get_hostnames(calico_nodes)),
                        target='tf_calico_hostnames')])

def get_hostnames(calico_nodes):
    hostnames = []
    if calico_nodes is not None:
        hostnames = [d['hostname'] for d in calico_nodes]
    return hostnames


def is_valid_hostname(hostname):
    '''Verify host name validity'''
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
            return redirect(f'/calico_nodes?fabric_type={fabric_type}')
    if request.method == 'GET':
        if fabric_type == "aci":
            l3out = json.loads(getdotenv('l3out'))
            ipv4_cluster_subnet = l3out['ipv4_cluster_subnet']
        elif fabric_type == "vxlan_evpn":
            overlay = json.loads(getdotenv('overlay'))
            ipv4_cluster_subnet = overlay["node_sub"]

        api_ip = str(ipaddress.IPv4Network(ipv4_cluster_subnet, strict=False).broadcast_address - 3)

        return render_template('cluster.html', api_ip=api_ip, k8s_ver=k8s_versions(), fabric_type=fabric_type)

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
            if vc['vm_deploy']:
                cluster = json.loads(getdotenv('cluster'))
                external_svc_subnet = req.get("ipv4_ext_svc_sub")
                cluster['pod_subnet'] = req.get("ipv4_pod_sub")
                cluster['external_svc_subnet'] = external_svc_subnet
                cluster['cluster_svc_subnet'] = req.get("ipv4_svc_sub")
                cluster['local_as'] = req.get("k8s_local_as")
                cluster['cni_plugin'] = req.get("cni_plugin")
                cluster['ingress_ip'] = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 1)
                cluster['visibility_ip'] = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 2)
                cluster['neo4j_ip'] = str(ipaddress.IPv4Interface(external_svc_subnet).ip + 3)
            else:
                cluster = create_cluster_vars()
                cluster['pod_subnet'] = req.get("ipv4_pod_sub")
                cluster['external_svc_subnet'] = req.get("ipv4_ext_svc_sub")
                cluster['cluster_svc_subnet'] = req.get("ipv4_svc_sub")
                cluster['local_as'] = req.get("k8s_local_as")
                cluster['cni_plugin'] = req.get("cni_plugin")
                if fabric_type == "aci":
                    l3out = json.loads(getdotenv('l3out'))
                    l3out['vlan_id'] = req.get("vlan_id")
                    if l3out['vlan_id'] == "" or int(l3out['vlan_id']) < 2 or int(l3out['vlan_id']) >4094:
                        logger.info('Invalid VLAN detected')
                        flash("Please Specify a valid VLAN ID (2-4094)")
                        return redirect(f'/cluster_network?fabric_type={fabric_type}')
                    logger.info('save l3out variable to update the VLAN ID in case of not VM Deployment')
                    setdotenv('l3out', json.dumps(l3out))
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
                return redirect(f'/fabric?fabric_type={fabric_type}')
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
        
        ipv4_cluster_subnet = None
        ipv6_cluster_subnet = None
        if fabric_type == "aci":
            ipv4_cluster_subnet=l3out['ipv4_cluster_subnet']
            ipv6_cluster_subnet=l3out['ipv6_cluster_subnet']
        elif fabric_type == "vxlan_evpn":
            ipv4_cluster_subnet=overlay["node_sub"]
            ipv6_cluster_subnet=overlay["node_sub_v6"]
        return render_template('cluster_network.html',
                                    ipv4_cluster_subnet=ipv4_cluster_subnet,
                                    ipv6_cluster_subnet=ipv6_cluster_subnet,
                                    ipv4_pod_sub=ipv4_pod_sub,
                                    ipv6_pod_sub=ipv6_pod_sub,
                                    ipv4_svc_sub=ipv4_svc_sub,
                                    ipv6_svc_sub=ipv6_svc_sub,
                                    ipv4_ext_svc_sub=ipv4_ext_svc_sub,
                                    ipv6_ext_svc_sub=ipv6_ext_svc_sub,
                                    k8s_local_as=k8s_local_as,
                                    vm_deploy=vc['vm_deploy'],
                                    fabric_type = fabric_type)

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
                if req.get("template"):
                    return redirect('/vctemplate')
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
            host = datastore.host[0].key
            resource_pool = vc_utils.get_largest_free_rp(si, datacenter, host)
            ova_path = str(os.getcwd()) + "/static/vm_templates/" + TEMPLATE_NAME + ".ova"
            ovf_handle = vc_utils.OvfHandler(ova_path)
            ovf_manager = si.content.ovfManager
            
            # Passing the first host connected to the datastore ensure we pick one of the host that will run the VM to validate the OVA
            #If we do not do this we pic a random host in the  resource pool
            if len(datastore.host) == 0:
                flash("No hosts connected to datastore ", req.get('datastore'))
                return redirect('/vctemplate')
            cisp = vc_utils.import_spec_params(entityName=TEMPLATE_NAME, diskProvisioning='thin',hostSystem=host)
            cisr = ovf_manager.CreateImportSpec(ovf_handle.get_descriptor(),resource_pool, datastore, cisp)

            if cisr.error:
                for error in cisr.error:
                    flash("The following errors will prevent import of this OVA: {}".format(error.msg), 'error')
                    return redirect('/vctemplate')
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
            upload.submit(vc_utils.start_upload, vc["url"], resource_pool,cisr, folder, ovf_handle,host)
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
            logger.error(e)
            flash(str(e), 'error')
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
                return redirect(f'/calico_nodes?fabric_type={fabric_type}')
        elif button == "Previous":
            return redirect(f'/vcenterlogin?fabric_type={fabric_type}')

        elif button == None and req.get("dc"):
            try:
                si = vc_utils.connect(vc["url"],  vc["username"], vc["pass"], '443')
            except gaierror as e:
                flash("Unable to connect to VC", 'error')
                return redirect(f'/vcenterlogin?fabric_type={fabric_type}')
            except Exception as e:
                flash(e.msg, 'error')
                return redirect(f'/vcenterlogin?fabric_type={fabric_type}')                   
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
            return redirect(f'/vcenterlogin?fabric_type={fabric_type}')
        except Exception as e:
            flash(e.msg, 'error')
            return redirect(f'/vcenterlogin?fabric_type={fabric_type}')

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
    def ipv6_status(req):
        if req.get("ipv6_cluster_subnet") == "":
            unsetdotenv('ipv6_enabled')
            return False
        else:
            logger.info('save ipv6_enabled variable')
            setdotenv('ipv6_enabled', "")
            return True
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
            ipv6_enabled = ipv6_status(req)
            mtu = int(req.get("mtu"))
            if mtu < 1280 or mtu > 9000:
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Error: Ivalid MTU, MTU must be >= 1280 and <= 9000")
            if req.get("anchor_nodes") == "":
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "At least one anchor node is required")
            if req.get("l3out_tenant") == "" or req.get("vrf_name") == "" or req.get("contract") == "" :
                return anchor_node_error(req.get("anchor_nodes"), session['pod_ids'], session['nodes_id'], str(rtr_id_counter), "Tenant, VRF, and Contract are mandatory parameters")

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
            
            rack_id = req.get("rack_id")
            rtr_id = req.get("rtr_id")
            primary_ip = req.get("node_ipv4")
            ipv6_enabled = ipv6_status(req)

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
                logger.info("Adding leaf v6")
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
                logger.info(node_ipv6)
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
    vc = getdotenvjson("vc")
    if not vc:
        vm_deploy = True
    else:
        vm_deploy = vc.get('vm_deploy')
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
        is_valid, message = validate_fabric_input(data)
        if not is_valid:
            return json.dumps({"error": escape(message)}), 400
        result = ndfc_process_fabric_setting(data)
        if result:
            return json.dumps({"ok": "fabric setting configured", "vm_deploy":vm_deploy}), 200
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
                subnet_v4 = str(ipaddress.IPv4Interface(item.gateway).network) if item.gateway else ""
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

def check_apic_user(apic):
    '''Check if a certificate based APIC user already exists'''
    logger.info('Check if certificate based APIC user already exists!')
    method = 'GET'
    path = '/api/node/class/infraCont.json'
    payload = ""
    try:
        with open('../ansible/roles/aci/files/'+apic['nkt_user']+'-user.key') as f:
            private_key_content = f.read()
    except FileNotFoundError:
        logger.info('Certificate based APIC user does not exits!')
        return False
    sig_key = load_privatekey(FILETYPE_PEM, private_key_content)
    sig_request = method + path + payload
    sig_signature = sign(sig_key, sig_request, "sha256")

    sig_dn = 'uni/userext/user-'+apic['nkt_user']+'/usercert-'+apic['nkt_user']+''
    headers = {}
    headers["Cookie"] = (
                "APIC-Certificate-Algorithm=v1.0; "
                + "APIC-Certificate-DN=%s; " % sig_dn
                + "APIC-Certificate-Fingerprint=fingerprint; "
                + "APIC-Request-Signature=%s" % base64.b64encode(sig_signature).decode("utf-8")
            )
    url = apic['url'] + path
    req = requests.get(url, headers=headers, data=payload, verify=False)
    if req.status_code == 200:
        logger.info('Certificate based APIC user already exists!')
        return True
    else:
        logger.info('Certificate based APIC user does not exits!')
        return False

def create_apic_user(apic):
    ''' Create Certificate based APIC user if is missing or not working'''
    if check_apic_user(apic):
        return 'OK'
    
    #In case we are accessing the create page directly a nkt_user is set but we need to gen generate a random pass
    # For it or APIC won't let us add a new user
    if 'nkt_user' in apic and 'nkt_pass' not in apic:
        apic['nkt_pass'] = get_random_string(20)
        setdotenv('apic', json.dumps(apic))
    logger.info('Create APIC User')
    ansible_output = ''
    ## Generate the inventory file for the APIC, this looks ugly might want to clean up
    config = f"""apic: #You ACI Fabric Name
    hosts:
        {apic['url'].replace("https://",'')}:
            validate_certs: no
            # APIC HTTPs Port
            port: 443
            # APIC user with admin credential
            admin_user: {apic['adminuser']}
            admin_pass: {apic['adminpass']}
            # APIC User that we create only for the duration of this playbook
            # We also create certificates for this user name to use cert based authentication
            aci_temp_username: {apic['nkt_user']}
            aci_temp_pass: "{apic['nkt_pass']}"
            """

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
        return 'OK'
    else:
        logger.info('Unable to create nkt user')
        return Response("Unable to create the nkt user\n Ansible Output provided for debugging:\n" + ansible_output, mimetype='text/event-stream')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Login page to get details for ACI or NDFC'''
    apic = {}
    vc = create_vc_vars()
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Login":
            apic['url'] = normalize_url(request.form['fabric'])
            apic['adminuser'] = request.form['username']
            apic['adminpass'] = request.form['password']
            apic['nkt_user'] = "nkt_user_" + get_random_string(6) #request.form['nkt_user']
            apic['nkt_pass'] = get_random_string(20, password=True)
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
                logger.error("Unable to connect to APIC")
                flash("Unable to connect to APIC", e)
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
            ret = create_apic_user(apic)
            if ret != 'OK':
                return ret
            return redirect('/l3out')

                
        if fabric_type == "vxlan_evpn":
            
            # NDC does not support yet selecting VM deployment option so settin it here to true
            vc['vm_deploy'] = request.json["deploy_vm"]
            ndfc = {}
            ndfc["url"] = normalize_url(request.json["url"])
            ndfc["username"] = request.json["username"]
            ndfc["password"] = request.json["password"]
            ndfc["platform"] = "nd"  # set to nd stattically
            inst_ndfc = NDFC(ndfc["url"], ndfc["username"], ndfc["password"])
            if not inst_ndfc.logon():
                return json.dumps({"error": "login fail"}), 400
            logger.info('login page: set ndfc and vc variable')
            setdotenv('ndfc', json.dumps(ndfc))
            setdotenv('vc', json.dumps(vc))
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
            del_files = []
            if os.path.exists(ANSIBLE_LOCK):
                os.remove(ANSIBLE_LOCK)
                del_files.append(ANSIBLE_LOCK)
            if fabric_type == "aci":
                if os.path.exists(TF_STATE_ACI):
                    os.remove(TF_STATE_ACI)
                    del_files.append(TF_STATE_ACI)
            if fabric_type == "vxlan_evpn":
                if os.path.exists(TF_STATE_NDFC):
                    os.remove(TF_STATE_NDFC)
                    del_files.append(TF_STATE_NDFC)
            if len(del_files) > 0:
                return Response("Deleted state files " + ', '.join(del_files))
            return Response("State files not found")
        except Exception:
           return Response("Reset Failed")

@app.route('/existing_cluster', methods=['GET', 'POST'])
@require_api_token
def existing_cluster():
    '''Page that detects an existing cluster and allow the user to destroy it'''
    fabric_type = get_fabric_type(request)
    if fabric_type not in VALID_FABRIC_TYPE:
        return redirect('/')
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Manage Nodes":
            return redirect(f'/calico_nodes?fabric_type={fabric_type}&manage=true')
    if request.method == "GET":
        if fabric_type == "aci":
            try:
                f = open("cluster.tfvars")
                current_config =  f.read()
                # Derive vkaci IP address:
                deployed_cluster = hcl2.loads(current_config)['vc']['vm_deploy']
                ext_ip = ""
                if deployed_cluster:
                    master = hcl2.loads(current_config)['calico_nodes'][0]
                    if master['natip'] != "":
                        ext_ip = master['natip']
                    else:
                        ext_ip = master['ip'].split("/")[0]

                vkaci_ui = "http://" + ext_ip + ":30000"
                # Do something with the file
            except IOError:
                return render_template('/existing_cluster.html', text_area_title="Error", config="Config File Not Found but terraform.tfstate file is present", vm_deploy=deployed_cluster)
            return render_template('/existing_cluster.html', text_area_title="Cluster Config:", config=current_config, vkaci_ui=vkaci_ui, vm_deploy=deployed_cluster)
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
        ansible_cmd = "ansible-playbook -i ../ansible/inventory/apic.yaml ../ansible/apic_user.yaml --tags='apic_user_del'"
        tf_cmd = "terraform destroy -auto-approve -no-color -var-file='cluster.tfvars'"
        cmds = [tf_cmd, ANSIBLE_LOCK_CMD, ansible_cmd, ANSIBLE_UNLOCK_CMD]
        g.run(["bash", "-c", ';'.join(filter(None, cmds))])
    elif fabric_type == "vxlan_evpn":
        integ_reset = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -b -i ../ansible/inventory/ndfc.yaml ../ansible/ndfc_integration.yaml -t reset"
        tf_destory = "terraform -chdir=ndfc destroy -auto-approve -no-color -var-file='cluster.tfvars'"
        if os.path.exists("../ansible/inventory/ndfc.yaml"):
            cmds = [ANSIBLE_LOCK_CMD, integ_reset, ANSIBLE_UNLOCK_CMD, tf_destory]
        else:
            cmds = [tf_destory]
        g.run(["bash", "-c", ';'.join(filter(None, cmds))])
    #p = g.run("ls")
    return Response(read_process(g), mimetype='text/event-stream')
def check_if_new_cluster():
        # if no tf state existed, return the intro page
    if not os.path.exists(TF_STATE_ACI) and not os.path.exists(TF_STATE_NDFC):
        return 'new'
    if os.path.exists(TF_STATE_ACI):
        with open('terraform.tfstate', 'r', encoding='utf-8') as f:
            state_aci = json.load(f)
        if state_aci['resources'] != []:
            return 'aci'

    if os.path.exists(TF_STATE_NDFC):
        with open('./ndfc/terraform.tfstate', 'r', encoding='utf-8') as f:
            state_ndfc = json.load(f)
            # If there are resources the cluster is there
        if state_ndfc['resources'] != []:
            return 'ndfc'
        # If the resources are not present go to intro
    return 'new'
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
        cluster_status = check_if_new_cluster()
        logger.info('cluster_status %s', cluster_status)
        # if no tf state existed, return the intro page
        if cluster_status == 'new':
            return render_template('intro.html')
        if cluster_status == 'aci':
            return redirect('/existing_cluster')
        if cluster_status == 'ndfc':
            return redirect('/existing_cluster?fabric_type=vxlan_evpn')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Nexus Kubernetes Tool allows you to configure your ACI/NDFC fabric and bootstrap a Kubernetes Cluster')
    parser.add_argument('-p', dest='port', type=int, default=80, help='The TCP port the webserver listens to')
    parser.add_argument('-d', dest='debug', action='store_true', default=False, help='Run Flask in debug mode')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=args.debug)
