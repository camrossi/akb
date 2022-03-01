import json
import requests
from requests.exceptions import ConnectionError
__author__ = "Shangxin Du(shdu@cisco.com)"


class Fabric:
    def __init__(self, name, dcnm):
        self._name = name
        self._dcnm = dcnm
        self._inventory = {}

    @property
    def name(self):
        return self._name

    @property
    def inventory(self):
        return self._inventory

    def get_inventory(self):
        inv_url = "/rest/control/fabrics/{}/inventory".format(self.name)
        inv = self._dcnm.rest(inv_url, "get")
        for sw in inv:
            self._inventory[sw["ipAddress"]] = sw
        return self._inventory

    def get_fabric_detail(self):
        url = "/rest/control/fabrics/" + self.name
        return self._dcnm.rest(url, "get")

    def discover_switch(self, switch, preserve_config=True):
        fabric_detail = self.get_fabric_detail()
        url = "/rest/control/fabrics/{}/inventory/test-reachability".format(fabric_detail["id"])
        data = {
            "seedIP": switch.address,
            "snmpV3AuthProtocol": "0",
            "username": switch.username,
            "password": switch.password,
            "maxHops": 0,
            "cdpSecondTimeout": "5",
            "preserveConfig": preserve_config
        }

        return self._dcnm.rest(url, "post", data)

    def register_switch(self, switch, preserve_config=True):
        fabric_detail = self.get_fabric_detail()
        discovered = self.discover_switch(switch, preserve_config=False)
        url = "/rest/control/fabrics/{}/inventory/discover".format(fabric_detail["id"])
        data = {
            "switches": [
                {
                    "sysName": discovered[0]["sysName"],
                    "ipaddr": switch.address,
                    "platform": discovered[0]["platform"],
                    "version": discovered[0]["version"],
                    "deviceIndex": discovered[0]["deviceIndex"]
                }
            ],
            "seedIP": switch.address,
            "snmpV3AuthProtocol": "0",
            "username": switch.username,
            "password": switch.password,
            "maxHops": 0,
            "cdpSecondTimeout": "5",
            "preserveConfig": preserve_config
        }
        return self._dcnm.rest(url, "post", data)

    def pre_provision(self, switches: list):
        url = "/rest/control/fabrics/{}/inventory/poap".format(self.name)
        data = []

        for sw in switches:
            poap_data = {
                "serialNumber": sw.sn,
                "model": sw.model,
                "version": sw.version,
                "hostname": sw.hostname,
                "ipAddress": sw.address,
                "password": sw.password,
                "data": json.dumps({"modulesModel": [sw.model], "gateway": sw.gateway}),
                "discoveryAuthProtocol": "0"
            }
            data.append(poap_data)

        return self._dcnm.rest(url, "post", data)

    def set_role(self, switch, role):
        self.get_inventory()
        url = "/rest/control/switches/roles"
        data = [
            {
                "serialNumber": self.inventory[switch.address]["serialNumber"],
                "role":role
            }
        ]
        return self._dcnm.rest(url, "post", data)

    def rediscover_switch(self, switch):
        self.get_inventory()
        url = "/rest/control/fabrics/{}/inventory/rediscover/{}".format(self.name, self.inventory[switch.address]["serialNumber"])
        return self._dcnm.rest(url, "post")

    def add_link(self, **kwargs):
        url = "/rest/control/links"
        data = {
            "sourceFabric": self.name,
            "destinationFabric": kwargs.get("dst_fabric", self.name),
            "sourceDevice": kwargs.get("src_sn"),
            "destinationDevice": kwargs.get("dst_sn"),
            "sourceSwitchName": kwargs.get("src_device"),
            "destinationSwitchName": kwargs.get("dst_device"),
            "sourceInterface": kwargs.get("src_int"),
            "destinationInterface": kwargs.get("dst_int"),
            "templateName": kwargs.get("template"),
            "nvPairs": kwargs.get("nvPairs", {})

        }
        return self._dcnm.rest(url, "post", data)

    def get_vrf_detail(self, vrf_name=None):
        url = "/rest/top-down/fabrics/{}/vrfs".format(self.name)
        result_list = []

        response = self._dcnm.rest(url, "get")
        if response:
            for item in response:
                if vrf_name and vrf_name != item["vrfName"]:
                    continue
                # no filter, return whole list
                template_config = json.loads(item["vrfTemplateConfig"])
                vrf = VRF(item["fabric"],
                          item["vrfName"],
                          item["vrfId"],
                          vlan_id=template_config['vrfVlanId'],
                          vrf_status=item['vrfStatus'],
                          template_config=template_config)
                result_list.append(vrf)

        return result_list

    def create_vrf(self, vrf):
        url = "/rest/top-down/fabrics/{}/vrfs".format(self.name)

        data = {
            "fabric": self.name,
            "vrfName": vrf.name,
            "vrfId": vrf.vrf_id,
            "vrfTemplateConfig": json.dumps(vrf.template_config),
            "vrfTemplate": vrf.template,
            "vrfExtensionTemplate": vrf.ext_template
        }
        return self._dcnm.rest(url, "post", data)

    def attach_vrf(self, vrf, switch_list, extend=None, peer_vrf=None):
        """
        attach vrf to provided list of switches
        params:
        vrf: str
            name of vrf
        switch_list: list
            list of switch mgmt ip address
        extend: None or VRF_LITE
            when attached to BL and need extend to external network
        """
        url = "/rest/top-down/fabrics/{}/vrfs/attachments".format(self.name)
        data = [{
            "vrfName": vrf.name,
            "lanAttachList": []
        }]
        vrf_detail = self.get_vrf_detail(vrf.name)

        inventory = self.get_inventory()
        switchs = [inventory[ip]["serialNumber"] for ip in switch_list]

        # if VRF_LITE extend is enabled, get interfaces that connect to core router
        # extend the vrf to external with provied peer vrf name
        if extend == "VRF_LITE" and not peer_vrf:
            raise ValueError("extend is enabled but peer vrf is not set")
        if extend == "VRF_LITE":
            extend_candidate = self.get_vrf_extension_prototype(self.name, vrf, switchs)
            extensions = {}
            for sw in extend_candidate[0]["switchDetailsList"]:
                extension_values = {
                    "VRF_LITE_CONN": {
                        "VRF_LITE_CONN": []
                    },
                    "MULTISITE_CONN": json.dumps({"MULTISITE_CONN": []})
                }
                if sw["serialNumber"] not in switchs:
                    continue
                intfs = sw["extensionPrototypeValues"]
                for intf in intfs:
                    res_dot1q = self.get_reserved_dot1q_id(vrf,
                                                           sw["serialNumber"],
                                                           intf["interfaceName"])
                    conn = json.loads(intf["extensionValues"])
                    # set proposed value and pop unused attr from prototype values
                    conn["DOT1Q_ID"] = res_dot1q
                    conn["PEER_VRF_NAME"] = peer_vrf
                    conn.pop("asn")
                    conn.pop("enableBorderExtension")
                    extension_values["VRF_LITE_CONN"]["VRF_LITE_CONN"].append(conn)
                extension_values["VRF_LITE_CONN"] = json.dumps({"VRF_LITE_CONN": extension_values["VRF_LITE_CONN"]["VRF_LITE_CONN"]})
                extensions[sw["serialNumber"]] = extension_values

        for sn in switchs:
            attach = {
                "fabric": self.name,
                "vrfName": vrf.name,
                "serialNumber": sn,
                "vlan": vrf_detail[0].vlan_id,
                "freeformConfig": "",
                # "extensionValues": json.dumps(extensions[sn]),
                "deployment": True
            }
            if extend == "VRF_LITE":
                attach["extensionValues"] = json.dumps(extensions[sn])
            data[0]['lanAttachList'].append(attach)
        return self._dcnm.rest(url, "post", data)

    def deploy_vrf(self, vrf):
        url = "/rest/top-down/fabrics/{}/vrfs/deployments".format(self.name)
        data = {
            "vrfNames": vrf
        }
        return self._dcnm.rest(url, "post", data)

    def get_vrf_extension_prototype(self, vrf, switch_list):
        """
        get extension prototype from switches
        params:
        vrf: str
            name of vrf
        switch_list: list
            list of SN
        """
        url = "/rest/top-down/fabrics/{}/vrfs/switches".format(self.name)
        data = {
            "vrf-names": vrf,
            "serial-numbers": ','.join(switch_list)
        }
        return self._dcnm.rest(url, "post", data)

    def get_reserved_dot1q_id(self, vrf, sn, intf):
        """
        get a reserved dot1q vlan for vrf-lite
        """
        url = "/rest/resource-manager/reserve-id"
        data = {
            "scopeType": "DeviceInterface",
            "usageType": "TOP_DOWN_L3_DOT1Q",
            "allocatedTo": vrf,
            "serialNumber": sn,
            "ifName": intf
        }
        return self._dcnm.rest(url, "post", data)

    def config_save(self):
        url = "/rest/control/fabrics/{}/config-save".format(self.name)
        return self._dcnm.rest(url, "post")

    def config_preview(self, switch=None):
        if not switch:
            url = "/rest/control/fabrics/{}/config-preview/".format(self.name)
        else:
            self.get_inventory()
            url = "/rest/control/fabrics/{}/config-preview/{}".format(self.name, self.inventory[switch.address]["serialNumber"])
        return self._dcnm.rest(url, "get")

    def config_deploy(self, switch=None):
        if not switch:
            url = "/rest/control/fabrics/{}/config-deploy".format(self.name)
        else:
            self.get_inventory()
            url = "/rest/control/fabrics/{}/config-deploy/{}".format(self.name, self.inventory[switch.address]["serialnumber"])
        return self._dcnm.rest(url, "post")


class Switch:
    def __init__(self, **kwargs):
        self._address = kwargs.get("address")
        self._username = kwargs.get("username")
        self._password = kwargs.get("password")
        self._role = kwargs.get("role", "Leaf")
        self._sn = kwargs.get("sn")
        self._model = kwargs.get("model")
        self._version = kwargs.get("version")
        self._hostname = kwargs.get("hostname")
        self._gateway = kwargs.get("gateway")

    @property
    def address(self):
        return self._address

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def role(self):
        return self._role

    @property
    def sn(self):
        return self._sn

    @property
    def model(self):
        return self._model

    @property
    def version(self):
        return self._version

    @property
    def hostname(self):
        return self._hostname

    @property
    def gateway(self):
        return self._gateway

    @role.setter
    def role(self, value):
        self._role = value


class Network:
    def __init__(self, fabric, name, seg_id, vrf, **kwargs):
        self._fabric = fabric
        self._name = name
        self._seg_id = seg_id
        self._vrf = vrf
        self._vlan_id = kwargs.get("vlan_id")
        self._gateway = kwargs.get("gateway")
        self._status = kwargs.get("network_status")
        if kwargs.get("template_config"):
            self._template_config = kwargs.get("template_config")
        else:
            self._template_config = {
                "vlanId": self._vlan_id,
                "gatewayIpAddress": kwargs.get("gateway")
            }

    @property
    def fabric(self):
        return self._fabric

    @property
    def name(self):
        return self._name

    @property
    def seg_id(self):
        return self._seg_id

    @property
    def vlan_id(self):
        return self._vlan_id

    @property
    def vrf(self):
        return self._vrf

    @property
    def gateway(self):
        return self._gateway

    @property
    def template_config(self):
        return self._template_config

    @property
    def status(self):
        return self._status


class VRF:
    def __init__(self,
                 fabric,
                 name,
                 vrf_id,
                 vlan_id,
                 vrf_status="NA",
                 template="Default_VRF_Universal",
                 ext_template="Default_VRF_Extension_Universal",
                 **kwargs):
        self._fabric = fabric
        self._name = name
        self._vrf_id = vrf_id
        self._vlan_id = vlan_id
        self._status = vrf_status
        self._template = template
        self._ext_template = ext_template
        self._template_config = {
            "vrfSegmentId": self._vrf_id,
            "vrfName": self._name,
            "vrfVlanId": self._vlan_id
        }
        for k in kwargs.keys():
            self._template_config[k] = kwargs[k]

    @property
    def fabric(self):
        return self._fabric

    @property
    def name(self):
        return self._name

    @property
    def vrf_id(self):
        return self._vrf_id

    @property
    def vlan_id(self):
        return self._vlan_id

    @property
    def status(self):
        return self._status

    @property
    def template_config(self):
        return self._template_config

    @property
    def template(self):
        return self._template

    @property
    def ext_template(self):
        return self._ext_template


class Template:
    def __init__(self, name, platforms, temp_type, temp_sub_type, **kwargs):
        self._name = name
        self._platforms = platforms
        self._temp_type = temp_type
        self._temp_sub_type = temp_sub_type
        self._content = kwargs.get("content", "")
        self._tags = kwargs.get("tags", "")

    @property
    def name(self):
        return self._name

    @property
    def platforms(self):
        return self._platforms

    @property
    def temp_type(self):
        return self._temp_type

    @property
    def temp_sub_type(self):
        return self._temp_sub_type

    @property
    def tags(self):
        return self._tags

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value


class NDFC:
    def __init__(self, url, username, password, verify=False):
        self._url = url
        self.username = username
        self.password = password
        self.verify = verify
        self._session = requests.session()
        self.headers = {
            "Content-Type": "application/json"
        }

    @property
    def url(self):
        return self._url

    @property
    def session(self):
        return self._session

    def logon(self):
        logon_url = self.url + "/login"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "userName": self.username,
            "userPasswd": self.password,
            "domain": "local"
        }
        try:
            response = self.session.post(logon_url,
                                         headers=headers,
                                         data=json.dumps(data),
                                         verify=False)
        except ConnectionError as e:
            print(e)
            return False
        if response.ok:
            return True
        else:
            return False

    def rest(self, url, method, data=None):
        rest_url = self.url + "/appcenter/cisco/ndfc/api/v1/lan-fabric" + url
        if "post" == method.lower():
            response = self.session.post(rest_url,
                                         headers=self.headers,
                                         data=json.dumps(data),
                                         verify=False)
            if response.ok:
                try:
                    return response.json()
                except json.decoder.JSONDecodeError:
                    return response.text
            else:
                print(response.text)
                return None
        if "get" == method.lower():
            response = self.session.get(rest_url,
                                        headers=self.headers,
                                        verify=self.verify)
            if response.ok:
                try:
                    return response.json()
                except json.decoder.JSONDecodeError:
                    return response.text
            else:
                print(response.text)
                return response

    def get_fabrics(self):
        # get all fabric from NDFC instance
        url = "/rest/control/fabrics"
        return self.rest(url, "get")

    def get_vrfs(self, fabric):
        # get all fabric from NDFC instance
        url = "/rest/top-down/fabrics/{}/vrfs".format(fabric)
        return self.rest(url, "get")

    def get_inventory(self, fabric):
        inv_url = self.url + "/rest/control/fabrics/{}/inventory".format(fabric.name)
        return self.rest(inv_url, "get")

    def discover_switch(self, switch, fabric, preserve_config=True):
        fabric_detail = self.get_fabric_detail(fabric)
        url = self.url + "/rest/control/fabrics/{}/inventory/test-reachability".format(fabric_detail["id"])
        data = {
            "seedIP": switch.address,
            "snmpV3AuthProtocol": "0",
            "username": switch.username,
            "password": switch.password,
            "maxHops": 0,
            "cdpSecondTimeout": "5",
            "preserveConfig": preserve_config
        }

        return self.rest(url, "post", data)

    def register_switch(self, switch, fabric, preserve_config=True):
        fabric_detail = self.get_fabric_detail(fabric)
        discovered = self.discover_switch(switch, fabric, preserve_config=False)
        url = self.url + "/rest/control/fabrics/{}/inventory/discover".format(fabric_detail["id"])
        data = {
            "switches": [
                {
                    "sysName": discovered[0]["sysName"],
                    "ipaddr": switch.address,
                    "platform": discovered[0]["platform"],
                    "version": discovered[0]["version"],
                    "deviceIndex": discovered[0]["deviceIndex"]
                }
            ],
            "seedIP": switch.address,
            "snmpV3AuthProtocol": "0",
            "username": switch.username,
            "password": switch.password,
            "maxHops": 0,
            "cdpSecondTimeout": "5",
            "preserveConfig": preserve_config
        }
        return self.rest(url, "post", data)

    def get_next_segid(self, fabric):
        seg_id_url = self.url + "/rest/managed-pool/fabrics/{}/segments/ids".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }

        response = requests.post(seg_id_url,
                                 headers=headers,
                                 verify=self.verify)
        if response.ok:
            return response.json()["segmentId"]
        else:
            return None

    def get_next_vrf_id(self, fabric):
        seg_id_url = self.url + "/rest/managed-pool/fabrics/{}/partitions/ids".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }

        response = requests.post(seg_id_url,
                                 headers=headers,
                                 verify=self.verify)
        if response.ok:
            return response.json()["partitionSegmentId"]
        else:
            return None

    def get_proposed_vlan(self, fabric, usage="network"):
        """
        get next available vlan based on usage
        Paras:
        fabric: str
            fabric name of vlan namespace
        usage: str, default=network
            usage of vlan, can be vrf or network, rest of input will be ignored and return none
        """
        topdown_vlan_url = self.url + "/rest/resource-manager/vlan/" + fabric
        headers = {
            "dcnm-token": self.token
        }

        if usage == "vrf":
            params = {"vlanUsageType": "TOP_DOWN_VRF_VLAN"}
        elif usage == "network":
            params = {"vlanUsageType": "TOP_DOWN_NETWORK_VLAN"}
        else:
            raise ValueError("usage {} is not valid".format(usage))

        response = requests.get(topdown_vlan_url,
                                headers=headers,
                                params=params,
                                verify=self.verify)
        if response.ok:
            return response.text
        else:
            return None

    def get_network_detail(self, fabric, network_name=None):
        network_detail_url = self.url + "/rest/top-down/fabrics/{}/networks".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }
        result_list = []

        response = requests.get(network_detail_url,
                                headers=headers,
                                verify=self.verify)
        if response.ok:
            for item in response.json():
                if network_name and network_name != item["networkName"]:
                    continue
                # no filter, return whole list
                template_config = json.loads(item["networkTemplateConfig"])
                network = Network(item["fabric"],
                                  item["networkName"],
                                  item["networkId"],
                                  template_config["vrfName"],
                                  vlan_id=template_config['vlanId'],
                                  network_status=item['networkStatus'],
                                  gateway=template_config["gatewayIpAddress"],
                                  template_config=template_config)
                result_list.append(network)

        return result_list

    def get_network_attachments(self, fabric, network):
        network_attach_url = self.url + "/rest/top-down/fabrics/{}/networks/attachments?network-names={}".format(fabric, network)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }

        response = requests.get(network_attach_url,
                                headers=headers,
                                verify=self.verify)
        if response.ok:
            return response.json()[0]['lanAttachList']
        else:
            return None

    def detach_network(self, fabric, network):
        detach_url = self.url + "/rest/top-down/fabrics/{}/networks/attachments".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }
        data = [{
            "networkName": network,
            "lanAttachList": []
        }]

        network_detail = self.get_network_detail(fabric, network)
        attach_list = self.get_network_attachments(fabric, network)
        switches = [sw["switchSerialNo"] for sw in attach_list if sw['isLanAttached']]
        for sn in switches:
            attach = {
                "fabric": fabric,
                "networkName": network,
                "serialNumber": sn,
                "switchPorts": "",
                "detachSwitchPorts": "",
                "vlan": network_detail[0].vlan_id,
                "dot1QVlan": 1,
                "untagged": False,
                "freeformConfig": "",
                "deployment": False
            }
            data[0]['lanAttachList'].append(attach)

        response = requests.post(detach_url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def create_network(self, network):
        create_network_url = self.url + "/rest/top-down/fabrics/{}/networks".format(network.fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }

        data = {
            "fabric": network.fabric,
            "vrf": network.vrf,
            "networkName": network.name,
            "networkId": network.seg_id,
            "networkTemplateConfig": json.dumps(network.template_config),
            "networkTemplate": "Default_Network_Universal",
            "networkExtensionTemplate": "Default_Network_Extension_Universal"
        }
        response = requests.post(create_network_url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def create_template(self, template):
        create_temp_url = self.url + "/fm/fmrest/config/templates/template"
        template_prop = """
##template properties \nname={};\ndescription = ;\ntags = {};\nuserDefined = true;\nsupportedPlatforms = {};\ntemplateType = {};\ntemplateSubType = {};\ncontentType = TEMPLATE_CLI;\nimplements = ;\ndependencies = ;\npublished = false;\n##\n
""".format(template.name,
           template.tags,
           template.platforms,
           template.temp_type,
           template.temp_sub_type)
        data = {
            "content": template_prop + template.content
        }
        response = requests.post(create_temp_url,
                                 headers=self.headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def delete_template(self, templates):
        delete_temp_url = self.url + "/fm/fmrest/config/templates/delete/bulk"
        data = {
            "name": [],
            "fabTemplate": templates
        }

        response = requests.post(delete_temp_url,
                                 headers=self.headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def attach_network(self, fabric, network, switch_list, interface_list, freeform_config):
        attach_url = self.url + "/rest/top-down/fabrics/{}/networks/attachments".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }
        data = [{
            "networkName": network,
            "lanAttachList": []
        }]
        network_detail = self.get_network_detail(fabric, network)

        inventory = self.get_inventory(fabric)
        switchs = [sw["serialNumber"] for sw in inventory if sw["ipAddress"] in switch_list]

        for sn in switchs:
            attach = {
                "fabric": fabric,
                "networkName": network,
                "serialNumber": sn,
                "switchPorts": ",".join(interface_list),
                "detachSwitchPorts": "",
                "vlan": network_detail[0].vlan_id,
                "dot1QVlan": 1,
                "untagged": False,
                "freeformConfig": "",
                "deployment": True
            }
            data[0]['lanAttachList'].append(attach)

        response = requests.post(attach_url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def attach_vrf(self, fabric, vrf, switch_list, extend=None, peer_vrf=None):
        """
        attach vrf to provided list of switches
        params:
        fabric: str
            name of fabric
        vrf: str
            name of vrf
        switch_list: list
            list of switch mgmt ip address
        extend: None or VRF_LITE
            when attached to BL and need extend to external network
        """
        attach_url = self.url + "/rest/top-down/fabrics/{}/vrfs/attachments".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }
        data = [{
            "vrfName": vrf,
            "lanAttachList": []
        }]
        vrf_detail = self.get_vrf_detail(fabric, vrf)

        inventory = self.get_inventory(fabric)
        switchs = [sw["serialNumber"] for sw in inventory if sw["ipAddress"] in switch_list]

        # if VRF_LITE extend is enabled, get interfaces that connect to core router
        # extend the vrf to external with provied peer vrf name
        if extend == "VRF_LITE" and not peer_vrf:
            raise ValueError("extend is enabled but peer vrf is not set")
        if extend == "VRF_LITE":
            extend_candidate = self.get_vrf_extension_prototype(fabric, vrf, switchs)
            extensions = {}
            for sw in extend_candidate[0]["switchDetailsList"]:
                extension_values = {
                    "VRF_LITE_CONN": {
                        "VRF_LITE_CONN": []
                    },
                    "MULTISITE_CONN": json.dumps({"MULTISITE_CONN": []})
                }
                if sw["serialNumber"] not in switchs:
                    continue
                intfs = sw["extensionPrototypeValues"]
                for intf in intfs:
                    res_dot1q = self.get_reserved_dot1q_id(vrf,
                                                           sw["serialNumber"],
                                                           intf["interfaceName"])
                    conn = json.loads(intf["extensionValues"])
                    # set proposed value and pop unused attr from prototype values
                    conn["DOT1Q_ID"] = res_dot1q
                    conn["PEER_VRF_NAME"] = peer_vrf
                    conn.pop("asn")
                    conn.pop("enableBorderExtension")
                    extension_values["VRF_LITE_CONN"]["VRF_LITE_CONN"].append(conn)
                extension_values["VRF_LITE_CONN"] = json.dumps({"VRF_LITE_CONN": extension_values["VRF_LITE_CONN"]["VRF_LITE_CONN"]})
                extensions[sw["serialNumber"]] = extension_values

        for sn in switchs:
            attach = {
                "fabric": fabric,
                "vrfName": vrf,
                "serialNumber": sn,
                "vlan": vrf_detail[0].vlan_id,
                "freeformConfig": "",
                # "extensionValues": json.dumps(extensions[sn]),
                "deployment": True
            }
            if extend == "VRF_LITE":
                attach["extensionValues"] = json.dumps(extensions[sn])
            data[0]['lanAttachList'].append(attach)
        response = requests.post(attach_url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def deploy_network(self, fabric, network):
        deploy_url = self.url + "/rest/top-down/fabrics/{}/networks/deployments".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }
        data = {
            "networkNames": network
        }

        response = requests.post(deploy_url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def deploy_vrf(self, fabric, vrf):
        deploy_url = self.url + "/rest/top-down/fabrics/{}/vrfs/deployments".format(fabric)
        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }
        data = {
            "vrfNames": vrf
        }

        response = requests.post(deploy_url,
                                 headers=headers,
                                 data=json.dumps(data),
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def save_n_deploy(self, fabric):
        save_url = self.url + "/rest/control/fabrics/core-virtual/config-save"
        deploy_url = self.url + "/rest/control/fabrics/core-virtual/config-deploy"

        headers = {
            "Content-Type": "application/json",
            "dcnm-token": self.token
        }

        response = requests.post(save_url,
                                 headers=headers,
                                 verify=self.verify)
        if not response.ok:
            print(response.text)
            return False

        response = requests.post(deploy_url,
                                 headers=headers,
                                 verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
            return False

    def delete_network(self, fabric, network):
        del_url = self.url + "/rest/top-down/fabrics/{}/networks/{}".format(fabric, network)

        headers = {
            "dcnm-token": self.token
        }

        response = requests.delete(del_url,
                                   headers=headers,
                                   verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)

    def delete_vrf(self, fabric, vrf):
        """
        delete vrf based on name
        params:
        fabric: str
            name of fabric
        vrf: str
            name of vrf
        """
        del_url = self.url + "/rest/top-down/fabrics/{}/vrfs/{}".format(fabric, vrf)

        headers = {
            "dcnm-token": self.token
        }

        response = requests.delete(del_url,
                                   headers=headers,
                                   verify=self.verify)
        if response.ok:
            return True
        else:
            print(response.text)
