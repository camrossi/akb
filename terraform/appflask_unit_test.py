
import pytest
from appflask import (is_valid_hostname, get_random_string, k8s_versions, 
                        normalize_url, get_fabric_type, create_vc_vars, 
                        create_l3out_vars, normalize_apt_mirror, get_manage_cluster, validate_fabric_input)


class Expando(object):
    pass


def get_request(fabric="", manage = None):
    request = Expando()
    request.args = {
        "fabric_type": fabric
    }
    if manage != None:
        request.args["manage"] = manage
    return request


@pytest.mark.parametrize("input,expected", [
    ("", False),
    (get_random_string(255), False),
    ("sammy.cisco.com", True)
])
def test_is_valid_hostname(input, expected):
    assert is_valid_hostname(input) == expected


@pytest.mark.parametrize("input,expected", [
    (get_request(""), "aci"),
    (get_request(None), "aci"),
    (get_request("SAM"), "sam"),
    (get_request("aci"), "aci"),
    (None, "aci"),
])
def test_get_fabric_type(input, expected):
    assert get_fabric_type(input) == expected


@pytest.mark.parametrize("input,expected", [
    ("192.168.1.1", "https://192.168.1.1"),
    ("http://192.168.1.1", "https://192.168.1.1"),
    ("http://192.168.1.1/", "https://192.168.1.1"),
    ("test-url/", "https://test-url"),
])
def test_normalize_url(input, expected):
    assert normalize_url(input) == expected


@pytest.mark.parametrize("input, expected", [
    (
        {
            'fabric_name': 'fabric-cylon',
            'asn': '65004',
            'vrf': '',
            'loopback_id': '100',
            'loopback_ipv4': [],
            'gateway_v4': '',
            'ibgp_peer_vlan': '3965',
            'route_tag': '65535',
            'ipv6_enabled': False,
            'bgp_pass': '',
            'k8s_integ': True
        },
        (False, "Invalid keys: ['vrf', 'loopback_ipv4', 'gateway_v4']")
    ),
    (
        {
            'fabric_name': 'fabric-cylon',
            'asn': '65004',
            'vrf': 'test',
            'loopback_id': '100',
            'loopback_ipv4': ["1.1.1.1"],
            'gateway_v4': '192.168.10.1/24',
            'gateway_v6': '',
            'ibgp_peer_vlan': '3965',
            'route_tag': '65535',
            'ipv6_enabled': True,
            'bgp_pass': '',
            'k8s_integ': True
        },
        (False, "Invalid keys: ['gateway_v6']")
    )
])
def test_validate_fabric_input(input, expected):
    assert validate_fabric_input(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("test.mirror.com", "https://test.mirror.com"),
        ("http://test.mirror.com", "http://test.mirror.com"),
        ("https://test.mirror.com/", "https://test.mirror.com/"),
        ("test-url/", "https://test-url/")
    ])
def test_normalize_apt_mirror(input, expected):
    assert normalize_apt_mirror(input) == expected


def test_create_VCVars():
    expected = {'url': 'test', 'username': 'test', 'pass': 'test', 'dc': 'test', 'datastore': 'test', 'cluster': 'test',
                'dvs': 'test', 'port_group': 'test', 'vm_template': 'test', 'vm_folder': 'test', 'vm_deploy': False}
    result = create_vc_vars("test", "test", "test", "test",
                          "test", "test", "test", "test", "test", "test", False)
    assert result == expected


def test_create_l3outVars():
    expected = {'name': 'test', 'l3out_tenant': 'test', 'vrf_tenant': 'name1', 'vrf_name': 'name2', 'node_profile_name': 'node_profile_FL3out', 'int_prof_name': 'int_profile_FL3out', 'int_prof_name_v6': 'int_profile_v6_FL3out', 'physical_dom': 'test', 'floating_ipv6': '2001:db8:abcd:11:ffff:ffff:ffff:ffff/128', 'secondary_ipv6': '2001:db8:abcd:11:ffff:ffff:ffff:fffe/128', 'floating_ip': '255.255.254.255/32',
                'secondary_ip': '255.255.254.254/32', 'def_ext_epg': 'test', 'def_ext_epg_scope': ['test', 'test', 'test'], 'local_as': 'test', 'mtu': 'test', 'bgp_pass': 'test', 'max_node_prefixes': '500', 'contract': 'contract2', 'contract_tenant': 'contract1', 'anchor_nodes': {}, 'ipv4_cluster_subnet': '255.255.255.0', 'ipv6_cluster_subnet': '2001:db8:abcd:12::/128', 'ipv6_enabled': True}
    result = create_l3out_vars(True, "test", "test", "name1/name2", "test",
                             "test", "255.255.255.0", "2001:db8:abcd:0012::0", "test", "test", "test", "test", "test", "test", "contract1/contract2", "{}")
    assert result == expected


def test_create_l3out_vars_invalid():
    '''invalid l3outVars'''
    expected = {'name': 'test', 'l3out_tenant': 'test', 'vrf_tenant': '', 'vrf_name': '',
                'node_profile_name': 'node_profile_FL3out', 'int_prof_name': 'int_profile_FL3out',
                'int_prof_name_v6': 'int_profile_v6_FL3out', 'physical_dom': 'test',
                'floating_ipv6': '2001:db8:abcd:11:ffff:ffff:ffff:ffff/128',
                'secondary_ipv6': '2001:db8:abcd:11:ffff:ffff:ffff:fffe/128',
                'floating_ip': '255.255.254.255/32',
                'secondary_ip': '255.255.254.254/32', 'def_ext_epg': 'test',
                'def_ext_epg_scope': ['test', 'test', 'test'], 'local_as': 'test',
                'mtu': 'test', 'bgp_pass': 'test', 'max_node_prefixes': '500', 'contract': '',
                'contract_tenant': '', 'anchor_nodes': {}, 'ipv4_cluster_subnet': '255.255.255.0',
                'ipv6_cluster_subnet': '2001:db8:abcd:12::/128', 'ipv6_enabled': True}
    result = create_l3out_vars(True, "test", "test", "t", "test",
                "test", "255.255.255.0", "2001:db8:abcd:0012::0", "test", "test", "test",
                "test", "test", "test", "c", "{}")
    assert result == expected

@pytest.mark.parametrize(
    "input,expected",
    [
        (get_request("",True), True),
        (get_request("","True"), True),
        (get_request("","true"), True),
        (get_request("", False), False),
        (get_request("", "1234"), False),
        (get_request("", 1234), False),
        (get_request("", None), False),
        (None, False),
    ])
def test_get_manage_cluster(input, expected):
    '''testing manage clusters'''
    assert get_manage_cluster(input) == expected


pytest.main()
