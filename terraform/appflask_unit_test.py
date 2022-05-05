
import pytest
from appflask import is_valid_hostname, \
    get_random_string, k8s_versions, normalize_url, \
    get_fabric_type, create_vc_vars, create_l3out_vars, \
    normalize_apt_mirror, validate_fabric_input


class Expando(object):
    pass


def get_request(fabric: str):
    request = Expando()
    request.args = {
        "fabric_type": fabric
    }
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


def test_k8s_versions():
    expected = ['1.23.4-00', '1.23.3-00', '1.23.2-00', '1.23.1-00', '1.23.0-00', '1.22.7-00', '1.22.6-00', '1.22.5-00', '1.22.4-00', '1.22.3-00', '1.22.2-00', '1.22.1-00', '1.22.0-00', '1.21.10-00', '1.21.9-00', '1.21.8-00', '1.21.7-00', '1.21.6-00', '1.21.5-00', '1.21.4-00', '1.21.3-00', '1.21.2-00', '1.21.1-00', '1.21.0-00', '1.20.15-00', '1.20.14-00', '1.20.13-00', '1.20.12-00', '1.20.11-00', '1.20.10-00', '1.20.9-00', '1.20.8-00', '1.20.7-00', '1.20.6-00', '1.20.5-00', '1.20.4-00', '1.20.2-00', '1.20.1-00', '1.20.0-00', '1.19.16-00', '1.19.15-00', '1.19.14-00', '1.19.13-00', '1.19.12-00', '1.19.11-00', '1.19.10-00', '1.19.9-00', '1.19.8-00', '1.19.7-00', '1.19.6-00', '1.19.5-00', '1.19.4-00', '1.19.3-00', '1.19.2-00', '1.19.1-00', '1.19.0-00', '1.18.20-00', '1.18.19-00', '1.18.18-00', '1.18.17-00', '1.18.16-00', '1.18.15-00', '1.18.14-00', '1.18.13-00', '1.18.12-00', '1.18.10-00', '1.18.9-00', '1.18.8-00', '1.18.6-00', '1.18.5-00', '1.18.4-01', '1.18.4-00', '1.18.3-00', '1.18.2-00', '1.18.1-00', '1.18.0-00', '1.17.17-00', '1.17.16-00', '1.17.15-00', '1.17.14-00', '1.17.13-00', '1.17.12-00', '1.17.11-00', '1.17.9-00', '1.17.8-00', '1.17.7-01', '1.17.7-00', '1.17.6-00', '1.17.5-00', '1.17.4-00', '1.17.3-00', '1.17.2-00', '1.17.1-00', '1.17.0-00', '1.16.15-00', '1.16.14-00', '1.16.13-00', '1.16.12-00', '1.16.11-01', '1.16.11-00', '1.16.10-00', '1.16.9-00', '1.16.8-00', '1.16.7-00', '1.16.6-00', '1.16.5-00', '1.16.4-00', '1.16.3-00', '1.16.2-00', '1.16.1-00', '1.16.0-00', '1.15.12-00', '1.15.11-00', '1.15.10-00', '1.15.9-00', '1.15.8-00', '1.15.7-00', '1.15.6-00', '1.15.5-00', '1.15.4-00', '1.15.3-00', '1.15.2-00', '1.15.1-00', '1.15.0-00', '1.14.10-00', '1.14.9-00', '1.14.8-00', '1.14.7-00', '1.14.6-00', '1.14.5-00', '1.14.4-00', '1.14.3-00', '1.14.2-00', '1.14.1-00',
                '1.14.0-00', '1.13.12-00', '1.13.11-00', '1.13.10-00', '1.13.9-00', '1.13.8-00', '1.13.7-00', '1.13.6-00', '1.13.5-00', '1.13.4-00', '1.13.3-00', '1.13.2-00', '1.13.1-00', '1.13.0-00', '1.12.10-00', '1.12.9-00', '1.12.8-00', '1.12.7-00', '1.12.6-00', '1.12.5-00', '1.12.4-00', '1.12.3-00', '1.12.2-00', '1.12.1-00', '1.12.0-00', '1.11.10-00', '1.11.9-00', '1.11.8-00', '1.11.7-00', '1.11.6-00', '1.11.5-00', '1.11.4-00', '1.11.3-00', '1.11.2-00', '1.11.1-00', '1.11.0-00', '1.10.13-00', '1.10.12-00', '1.10.11-00', '1.10.10-00', '1.10.9-00', '1.10.8-00', '1.10.7-00', '1.10.6-00', '1.10.5-00', '1.10.4-00', '1.10.3-00', '1.10.2-00', '1.10.1-00', '1.10.0-00', '1.9.11-00', '1.9.10-00', '1.9.9-00', '1.9.8-00', '1.9.7-00', '1.9.6-00', '1.9.5-00', '1.9.4-00', '1.9.3-00', '1.9.2-00', '1.9.1-00', '1.9.0-00', '1.8.15-00', '1.8.14-00', '1.8.13-00', '1.8.12-00', '1.8.11-00', '1.8.10-00', '1.8.9-00', '1.8.8-00', '1.8.7-00', '1.8.6-00', '1.8.5-01', '1.8.5-00', '1.8.4-01', '1.8.4-00', '1.8.3-01', '1.8.3-00', '1.8.2-01', '1.8.2-00', '1.8.1-01', '1.8.1-00', '1.8.0-01', '1.8.0-00', '1.7.16-00', '1.7.15-00', '1.7.14-00', '1.7.11-01', '1.7.11-00', '1.7.10-01', '1.7.10-00', '1.7.9-01', '1.7.9-00', '1.7.8-01', '1.7.8-00', '1.7.7-01', '1.7.7-00', '1.7.6-01', '1.7.6-00', '1.7.5-01', '1.7.5-00', '1.7.4-01', '1.7.4-00', '1.7.3-02', '1.7.3-01', '1.7.2-01', '1.7.2-00', '1.7.1-01', '1.7.1-00', '1.7.0-01', '1.7.0-00', '1.6.13-01', '1.6.13-00', '1.6.12-01', '1.6.12-00', '1.6.11-01', '1.6.11-00', '1.6.10-01', '1.6.10-00', '1.6.9-01', '1.6.9-00', '1.6.8-01', '1.6.8-00', '1.6.7-01', '1.6.7-00',
                '1.6.6-01', '1.6.6-00', '1.6.5-01', '1.6.5-00', '1.6.4-01', '1.6.4-00', '1.6.3-01', '1.6.3-00', '1.6.2-01', '1.6.2-00', '1.6.1-01', '1.6.1-00', '1.6.0-01', '1.6.0-00', '1.5.7-01', '1.5.7-00', '1.5.6-01', '1.5.6-00', '1.5.3-01', '1.5.3-00', '1.5.2-01', '1.5.2-00', '1.5.1-01', '1.5.1-00']
    result = k8s_versions()
    assert result == expected


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


def test_create_l3outVars_invalid():
    expected = {'name': 'test', 'l3out_tenant': 'test', 'vrf_tenant': '', 'vrf_name': '', 'node_profile_name': 'node_profile_FL3out', 'int_prof_name': 'int_profile_FL3out', 'int_prof_name_v6': 'int_profile_v6_FL3out', 'physical_dom': 'test', 'floating_ipv6': '2001:db8:abcd:11:ffff:ffff:ffff:ffff/128', 'secondary_ipv6': '2001:db8:abcd:11:ffff:ffff:ffff:fffe/128', 'floating_ip': '255.255.254.255/32',
                'secondary_ip': '255.255.254.254/32', 'def_ext_epg': 'test', 'def_ext_epg_scope': ['test', 'test', 'test'], 'local_as': 'test', 'mtu': 'test', 'bgp_pass': 'test', 'max_node_prefixes': '500', 'contract': '', 'contract_tenant': '', 'anchor_nodes': {}, 'ipv4_cluster_subnet': '255.255.255.0', 'ipv6_cluster_subnet': '2001:db8:abcd:12::/128', 'ipv6_enabled': True}
    result = create_l3out_vars(True, "test", "test", "t", "test",
                             "test", "255.255.255.0", "2001:db8:abcd:0012::0", "test", "test", "test", "test", "test", "test", "c", "{}")
    assert result == expected


pytest.main()
