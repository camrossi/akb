import json
from shelljob import proc
from gevent import monkey; monkey.patch_all()
from flask import Flask, Response, request, render_template, stream_with_context, session, redirect
from gevent.pywsgi import WSGIServer
from logging.config import dictConfig
import webbrowser
import string
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import requests

l3out = {}
vc = {}
cluster = {}
calico_nodes = ""
apic = ""
apic_username = ""
apic_password = ""

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

#app = Flask(__name__)
app = Flask(__name__, template_folder='./TEMPLATES/')
app.config['SECRET_KEY'] = 'cisco'


class LoginForm(FlaskForm):
    fabric = StringField('FabricIP', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

def getAPICCookie():
    url = 'https://'+session['fabric']+'/api/aaaLogin.xml'
    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (
        session['username'], session['password'])
    req = requests.post(url, data=xml_string, verify=False)
    session['cookie'] = req.cookies['APIC-cookie']


def sendAPICRequest(apicurl):
    url = 'https://'+session['fabric']+apicurl
    cookies = {}
    cookies['APIC-cookie'] = session['cookie']
    req = requests.get(url, cookies=cookies, verify=False)
    return json.loads(req.text)


def createl3outVars(l3out_tenant, name, vrf_name, vrf_tenant, physical_dom, floating_ipv6, secondary_ipv6, floating_ip, secondary_ip, vlan_id, def_ext_epg, def_ext_epg_scope: list, local_as, bgp_pass, contract, dns_servers, dns_domain, anchor_nodes):
    def_ext_epg_scope = list(def_ext_epg_scope.split(","))
    dns_servers = list(dns_servers.split(","))
    anchor_nodes = json.loads(anchor_nodes)
    app.logger.info(anchor_nodes)
    l3out =  {"name":name,"l3out_tenant":l3out_tenant,"vrf_tenant":vrf_tenant,"vrf_name":vrf_name,"node_profile_name":"node_profile_FL3out","int_prof_name":"int_profile_FL3out","int_prof_name_v6":"int_profile_v6_FL3out","physical_dom":physical_dom,"floating_ipv6":floating_ipv6,"secondary_ipv6":secondary_ipv6,"floating_ip":floating_ip,"secondary_ip":secondary_ip,"vlan_id":vlan_id,"def_ext_epg":def_ext_epg,"def_ext_epg_scope":def_ext_epg_scope,"local_as":local_as,"mtu":"9000","bgp_pass":bgp_pass,"max_node_prefixes":"500",'contract':contract,"dns_servers":dns_servers,"dns_domain":dns_domain,"anchor_nodes":anchor_nodes}
    return l3out

def createVCVars(url, username, passw, dc, datastore, cluster, dvs, port_group, vm_template, vm_folder):
    vc =  {"url":url,"username":username,"pass":passw,"dc":dc,"datastore":datastore,"cluster":cluster,"dvs":dvs,"port_group":port_group,"vm_template":vm_template,"vm_folder":vm_folder}
    return vc

def createClusterVars(control_plane_vip,ntp_server,http_proxy_status,http_proxy,node_sub,node_sub_v6):
    cluster =  {"control_plane_vip":control_plane_vip,"ntp_server":ntp_server,"http_proxy_status":http_proxy_status,"http_proxy":http_proxy,"node_sub":node_sub,"node_sub_v6":node_sub_v6,"kube_version":"1.22.1-00","crio_version":"1.21","OS_Version":"xUbuntu_20.04","vip_port":"8443","haproxy_image":"haproxy:2.3.6","keepalived_image":"osixia/keepalived:2.0.20","keepalived_router_id":"51","kubeadm_token":"fqv728.htdmfzf6rt9blhej","pod_subnet":"10.1.0.0/16","pod_subnet_v6":"2001:db8:43::/56","cluster_svc_subnet":"192.168.8.0/22","cluster_svc_subnet_v6":"2001:db8:44:1::/112","external_svc_subnet":"192.168.3.0/24","external_svc_subnet_v6":"2001:db8:44:2::/112","ingress_ip":"192.168.3.1","time_zone":"Europe/Rome","docker_mirror":"10.67.185.120:5000"}
    return cluster

def createCalicoNodes(calico_nodes):
    calicoNodes = json.loads(calico_nodes)
    return calicoNodes

@app.route( '/calico_nodes', methods=['GET', 'POST'] )
def stream():
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        global calico_nodes
        g = proc.Group()
        def read_process():
                while g.is_pending():   
                    lines = g.readlines()
                    for proc, line in lines:
                        _data = line.decode('utf8')
                        #_data = _data.decode('utf8')
                        yield _data+'\n'
        if button == "Create":            
            calico_nodes = createCalicoNodes(req.get("calico_nodes"))

            approve = {"auto-approve": True}
            g = proc.Group()
            app.logger.info(json.dumps(l3out))
            app.logger.info(json.dumps(vc))
            app.logger.info(json.dumps(cluster))
            app.logger.info(json.dumps(calico_nodes))
            p1 = g.run(["bash", "-c", "terraform apply -no-color -auto-approve -var 'l3out="+json.dumps(l3out)+"' -var 'vc="+json.dumps(vc)+"' -var 'k8s_cluster="+json.dumps(cluster)+"' -var 'calico_nodes="+json.dumps(calico_nodes)+"'"])
            #p1 = g.run(["bash", "-c", "terraform apply -no-color -auto-approve -var 'l3out="+json.dumps(l3out)+"' -var 'vc="+json.dumps(vc)+"' -var 'k8s_cluster="+json.dumps(cluster)+"'"])
            #p1 = g.run(["bash", "-c", "terraform apply -no-color -auto-approve -var 'l3out="+json.dumps(l3out)+"' -var 'vc="+json.dumps(vc)+"'"])
            #p1 = g.run(["bash", "-c", "terraform apply -no-color -auto-approve -var 'l3out="+json.dumps(l3out)+"'"])

            #p1 = g.run(["bash", "-c", "terraform plan -no-color"])

            #return webbrowser.open(/terraform)
            return Response( read_process(), mimetype= 'text/event-stream' )
        if button == "Destroy":
            p1 = g.run(["bash", "-c", "terraform destroy -no-color -auto-approve"])
            return Response( read_process(), mimetype= 'text/event-stream' )
    if request.method == 'GET':
        return render_template('calico_nodes.html')


@app.route( '/cluster', methods=['GET', 'POST'] )
def cluster():
    #app.logger.info(apic+apic_password+apic_username)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next": 
            global cluster
            cluster = createClusterVars(req.get("control_plane_vip"),req.get("ntp_server"),req.get("http_proxy_status"),req.get("http_proxy"),req.get("node_sub"),req.get("node_sub_v6"))
            return redirect('/calico_nodes')
        if button == "Previous":
            return redirect('/vcenter')      
    if request.method == 'GET':
        return render_template('cluster.html')


@app.route( '/vcenter', methods=['GET', 'POST'] )
def vcenter():
    #app.logger.info(apic+apic_password+apic_username)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next": 
            global vc
            vc = createVCVars(req.get("url"), req.get("username"), req.get("pass"), req.get("dc"), req.get("datastore"), req.get("cluster"), req.get("dvs"), req.get("port_group"), req.get("vm_template"), req.get("vm_folder"))
            return redirect('/cluster')
        if button == "Previous":
            return redirect('/l3out')   
    if request.method == 'GET':
        return render_template('vcenter.html')


@app.route( '/l3out', methods=['GET', 'POST'] )
def l3out():
    #app.logger.info(apic+apic_password+apic_username)
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        if button == "Next": 
            global l3out
            l3out = createl3outVars(req.get("l3out_tenant"),req.get("name"),req.get("vrf_name"),req.get("vrf_tenant"),req.get("physical_dom"),req.get("floating_ipv6"),req.get("secondary_ipv6"),req.get("floating_ip"),req.get("secondary_ip"),req.get("vlan_id"),req.get("def_ext_epg"),req.get("def_ext_epg_scope"),req.get("local_as"),req.get("bgp_pass"),req.get("contract"),req.get("dns_servers"),req.get("dns_domain"),req.get("anchor_nodes"))
            return redirect('/vcenter')
        if button == "Previous":
            return redirect('/login')   
    if request.method == 'GET':
        return render_template('l3out.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global apic
    global apic_username
    global apic_password
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Login": 
            apic = request.form['fabric']
            apic_username = request.form['username']
            apic_password = request.form['password']
            return redirect('/l3out')
        if button == "Previous":
            return redirect('/intro')   
    return render_template('login.html')

@app.route('/')
@app.route('/intro', methods=['GET', 'POST'] )
def get_page():
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        if button == "Go":
            return redirect('/login')
    return render_template('intro.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0' , port=5002, debug=True)