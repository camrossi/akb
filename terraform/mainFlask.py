import requests
import os
import sys
import json
from flask import render_template, flash, redirect, request, session
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from python_terraform import *

from logging.config import dictConfig

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

app = Flask(__name__, template_folder='./TEMPLATES/')
app.config['SECRET_KEY'] = 'cisco'

def terraformAction(action, l3out_tenant, name, vrf_name, vrf_tenant, physical_dom, floating_ipv6, secondary_ipv6, floating_ip, secondary_ip, vlan_id, dns_servers, dns_domain):
    approve = {"auto-approve": True}
    tf = Terraform(working_dir='./', variables={
                   'l3out_tenant': l3out_tenant, 'name': name, 'vrf_name': vrf_name, 'vrf_tenant': vrf_tenant, 'physical_dom': physical_dom, 'floating_ipv6': floating_ipv6, 'secondary_ipv6': secondary_ipv6, 'floating_ip': floating_ip, 'secondary_ip': secondary_ip, 'vlan_id': vlan_id, 'dns_servers': dns_servers, 'dns_domain': dns_domain, })
    if action != 'destroy':
        app.logger.info("-- executing tf.plan and apply")
        plan = tf.plan(no_color=IsFlagged, refresh=False,
                       capture_output=True, out="plan.out")
        output = tf.apply(skip_plan=True, **approve, capture_output=True)
    else:
        app.logger.info("-- executing tf.destroy")
        output = tf.destroy(variables={'l3out_tenant': l3out_tenant, 'name': name, 'vrf_name': vrf_name, 'vrf_tenant': vrf_tenant, 'physical_dom': physical_dom, 'floating_ipv6': floating_ipv6, 'secondary_ipv6': secondary_ipv6, 'floating_ip': floating_ip, 'secondary_ip': secondary_ip, 'vlan_id': vlan_id, 'dns_servers': dns_servers, 'dns_domain': dns_domain, }, force=IsNotFlagged, **approve)
        app.logger.info(output)
    return output

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


@app.route('/terraform', methods=['GET', 'POST'])
def terraform():
    if request.method == "POST":
        req = request.form
        button = req.get("button")
        app.logger.info(button)
        if button == "Create":
            app.logger.info("-- creating")
            planOutput = terraformAction("create",req.get("l3out_tenant"),req.get("name"),req.get("vrf_name"),req.get("vrf_tenant"),req.get("physical_dom"),req.get("floating_ipv6"),req.get("secondary_ipv6"),req.get("floating_ip"),req.get("secondary_ip"),req.get("vlan_id"),req.get("dns_servers"),req.get("dns_domain"))
            return render_template('terraform.html', plan=planOutput)
        elif button == "Destroy":
            app.logger.info("-- destroying")
            planOutput = terraformAction("destroy", '','','')
            return render_template('terraform.html', plan=planOutput)
        elif True: 
            return request.form
    return render_template('terraform.html')


@app.route('/menu')
def menu():
    return render_template('menu.html')



@app.route('/')
@app.route('/index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        session['fabric'] = request.form['fabric']
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        try:
            getAPICCookie()
            if 'cookie' in session:
                return redirect('/menu')
        except KeyError:
            flash('Invalid credentials')
            return redirect('login')
    return render_template('login.tpl', title='Sign In')


if __name__ == '__main__':
    app.run(host='0.0.0.0' , port=80)
