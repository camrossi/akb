import json
from shelljob import proc
from gevent import monkey; monkey.patch_all()
from flask import Flask, Response, request, render_template, stream_with_context
from gevent.pywsgi import WSGIServer
from logging.config import dictConfig
import webbrowser


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

app = Flask(__name__)


def createPlanVars(l3out_tenant, name, vrf_name, vrf_tenant, physical_dom, floating_ipv6, secondary_ipv6, floating_ip, secondary_ip, vlan_id, dns_servers, dns_domain):
    l3out =  {"name":name,"l3out_tenant":l3out_tenant,"vrf_tenant":vrf_tenant,"vrf_name":vrf_name,"node_profile_name":"node_profile_FL3out","int_prof_name":"int_profile_FL3out","int_prof_name_v6":"int_profile_v6_FL3out","physical_dom":physical_dom,"floating_ipv6":floating_ipv6,"secondary_ipv6":secondary_ipv6,"floating_ip":floating_ip,"secondary_ip":secondary_ip,"vlan_id":vlan_id,"def_ext_epg":"catch_all","def_ext_epg_scope":['import-security','shared-security','shared-rtctrl'],"local_as":"65534","mtu":"9000","bgp_pass":"123Cisco123","max_node_prefixes":"500",'contract':"k8s","dns_servers":['10.48.170.50','144.254.71.184'],"dns_domain":dns_domain,"anchor_nodes":[{"node_id":"101","pod_id":"1","rtr_id":"1.1.4.201","primary_ip":"192.168.2.101/24","primary_ipv6":"2001:db8:42::201/56","rack_id":"1"},{"node_id":"102","pod_id":"1","rtr_id":"1.1.4.202","primary_ip":"192.168.2.102/24","rack_id":"1","primary_ipv6":"2001:db8:42::202/56"}]}
    return l3out

@app.route( '/terraform', methods=['GET', 'POST'] )
def stream():
    if request.method == 'POST':
        req = request.form
        button = req.get("button")
        g = proc.Group()
        def read_process():
                while g.is_pending():   
                    lines = g.readlines()
                    for proc, line in lines:
                        _data = line.decode('utf8')
                        #_data = _data.decode('utf8')
                        yield _data+'\n'
        if button == "Create":
            l3out = createPlanVars(req.get("l3out_tenant"),req.get("name"),req.get("vrf_name"),req.get("vrf_tenant"),req.get("physical_dom"),req.get("floating_ipv6"),req.get("secondary_ipv6"),req.get("floating_ip"),req.get("secondary_ip"),req.get("vlan_id"),req.get("dns_servers"),req.get("dns_domain"))
            approve = {"auto-approve": True}
            g = proc.Group()
            app.logger.info(json.dumps(l3out))
            p1 = g.run(["bash", "-c", "terraform apply -no-color -auto-approve -var 'l3out="+json.dumps(l3out)+"'"])
            #p1 = g.run(["bash", "-c", "terraform plan -no-color"])

            #return webbrowser.open(/terraform)
            return Response( read_process(), mimetype= 'text/event-stream' )
        if button == "Destroy":
            p1 = g.run(["bash", "-c", "terraform destroy -no-color -auto-approve"])
            return Response( read_process(), mimetype= 'text/event-stream' )
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/')
def get_page():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0' , port=5000)
    app.run(debug=True)