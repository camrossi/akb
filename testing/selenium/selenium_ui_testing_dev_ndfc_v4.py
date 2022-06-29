from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import argparse
from time import sleep
from selenium_utils import wait_for_clickable

def check_exits_by_id(driver, id):
    '''Test check html element exists by id'''
    try:
        driver.find_element(By.ID, id)
    except NoSuchElementException:
        return False
    return True

def wait_for_title(driver, title):
    WebDriverWait(driver, 30).until(lambda x: title in x.title )

def add_calico_node(driver, hostname, ip, rack_id):
    elem = driver.find_element(By.NAME, "hostname")
    elem.clear()
    elem.send_keys(hostname)
    elem = driver.find_element(By.NAME, "ip")
    elem.clear()
    elem.send_keys(ip)
    elem = driver.find_element(By.NAME, "ipv6")
    elem.clear()
    elem = driver.find_element(By.NAME, "rack_id")
    elem.clear()
    elem.send_keys(rack_id)
    elem = driver.find_element(By.ID, "add_node")
    elem.click()
    wait_for_clickable(driver,(By.ID,"add_node"))

def fill_by_id(driver, id, value):
    elem = driver.find_element(By.ID, id)
    elem.clear()
    elem.send_keys(value)
    return elem


def root_page(driver):
    wait_for_title(driver, "NKT")
    select = Select(driver.find_element(By.ID, 'fabric_type'))
    select.select_by_visible_text("NDFC/VXLAN_EVPN")
    elem = driver.find_element(By.NAME, "button")
    current_url = driver.current_url
    elem.click()
    WebDriverWait(driver, 60).until(EC.url_changes(current_url))


def login_page(driver):
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    fill_by_id(driver, "url", "172.25.74.47")
    fill_by_id(driver, "username", "admin")
    fill_by_id(driver, "password", "ins3965!")
    elem = driver.find_element(By.NAME, "button")
    elem.click()
    WebDriverWait(driver, 60).until(EC.url_changes(current_url))


def fabric_page(driver):
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    fill_by_id(driver, "fabric", "fabric-cylon")
    sleep(2)
    fill_by_id(driver, "vrf", "k8s_cluster")
    fill_by_id(driver, "network", "network_k8s_test")
    sleep(2)
    fill_by_id(driver, "loopback_id", "90")

    lo = fill_by_id(driver, "input_lo_ipv4", "1.1.1.1")
    lo.send_keys(Keys.ENTER)
    lo = fill_by_id(driver, "input_lo_ipv4", "1.1.1.2")
    lo.send_keys(Keys.ENTER)
    # WebDriverWait(driver, 60).until(EC.url_changes(current_url))

    adv = driver.find_element(By.ID, "ck_box_k8s_integ")
    adv.click()

    adv = driver.find_element(By.ID, "advanced")
    adv.click()
    fill_by_id(driver, "ibgp_peer_vlan", "3960")
    fill_by_id(driver, "route_map", "k8s_ci_route_map")
    fill_by_id(driver, "loopback_route_tag", "487321")

    # add leaf nodes
    vpc = Select(driver.find_element(By.ID, "vpc_peer"))
    vpc.select_by_visible_text("93240YC-FX2-L02-S4/93240YC-FX2-L01-S4")
    elem = fill_by_id(driver, "primary_ipv4", "192.168.20.1/30")
    elem.send_keys(Keys.TAB)
    elem = driver.find_element(By.ID, "add_node")
    elem.click()
    vpc.select_by_visible_text("93180YC-FX-L04-S4/93180YC-FX-L03-S4")
    elem = fill_by_id(driver, "primary_ipv4", "192.168.20.5/30")
    elem.send_keys(Keys.TAB)
    elem = driver.find_element(By.ID, "add_node")
    elem.click()

    elem = driver.find_element(By.ID, "next")
    elem.click()
    WebDriverWait(driver, 60).until(EC.url_changes(current_url))


def vcenter_login_page(driver):
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    fill_by_id(driver, "url", "172.25.74.45")
    fill_by_id(driver, "username", "admin")
    fill_by_id(driver, "pass", "ins3965!")
    upload = driver.find_element(By.ID, "template_checkbox")
    upload.click()
    elem = driver.find_element(By.ID, "submit")
    elem.click()
    WebDriverWait(driver, 60).until(EC.url_changes(current_url))


def vcenter_page(driver):
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    select = Select(driver.find_element(By.ID, 'dc'))
    select.select_by_visible_text("dc-cylon")

    # Wait for vCenter API to populate the page
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="vms_list"]/option[1]')))
    except ValueError as e:
        print(e)
        print("Loading took too much time!")

    #elem = driver.find_element(By.ID, 'datastore')
    #elem.send_keys("vsan_datastore")
    select = Select(driver.find_element(By.ID, 'cluster'))
    select.select_by_visible_text("cluster-cylon")
    elem = driver.find_element(By.ID, 'port_group')
    elem.send_keys("dvs-cylon/network_k8s_test/vlan-210")
    elem = driver.find_element(By.ID, 'vm_templates')
    elem.send_keys("nkt_template")
    elem = driver.find_element(By.ID, 'vm_folder')
    elem.send_keys("NKT_CI")
    elem = driver.find_element(By.ID, "submit")
    elem.click()
    WebDriverWait(driver, 60).until(EC.url_changes(current_url))


def calico_node_page(driver):
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    elem = driver.find_element(By.ID, 'calico_nodes')
    elem.clear()

    add_calico_node(driver, 'gitaction-nkt-master-1', '10.15.0.1/24', '1')
    add_calico_node(driver, 'gitaction-nkt-master-2', '10.15.0.2/24', '1')
    add_calico_node(driver, 'gitaction-nkt-master-3', '10.15.0.3/24', '1')
    add_calico_node(driver, 'gitaction-nkt-worker-1', '10.15.0.4/24', '1')
    add_calico_node(driver, 'gitaction-nkt-worker-2', '10.15.0.5/24', '1')
    add_calico_node(driver, 'gitaction-nkt-worker-3', '10.15.0.6/24', '1')
    elem = driver.find_element(By.ID, "submit")
    current_url = driver.current_url
    elem.click()

    WebDriverWait(driver, 60).until(EC.url_changes(current_url))


def cluster_page(driver):
    wait_for_title(driver, "Cluster")
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    elem = driver.find_element(By.ID, 'advanced')
    elem.click()

    fill_by_id(driver, "timezone", "America/Los_Angeles")
    fill_by_id(driver, "dns_servers", "10.195.200.67")
    fill_by_id(driver, "dns_domain", "cisco.com")
    fill_by_id(driver, "docker_mirror", "registry-shdu.cisco.com")
    fill_by_id(driver, "ntp_servers", "10.195.225.200")
    fill_by_id(driver, "ubuntu_apt_mirror", "dal.mirrors.clouvider.net/ubuntu/")

    elem = driver.find_element(By.ID, "submit")
    elem.click()

    WebDriverWait(driver, 60).until(EC.url_changes(current_url))


def cluster_network_page(driver):
    wait_for_title(driver, "Cluster Network")
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    elem = driver.find_element(By.ID, "submit")
    current_url = driver.current_url
    elem.click()

    WebDriverWait(driver, 60).until(EC.url_changes(current_url))

def create_page(driver):
    '''test create page'''
    current_url = driver.current_url
    wait_for_title(driver, "Create")
    assert "fabric_type=vxlan_evpn" in current_url
    assert check_exits_by_id(driver, "vkaci") is False

def assert_ndfc(driver, title) -> str:
    '''Assert that vdfc fabric type is in the url with page title'''
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    wait_for_title(driver,title)
    return current_url

def click_previous(driver, url):
    '''Click the previous button'''
    elem = driver.find_element(By.ID,'Previous')
    elem.click()
    WebDriverWait(driver, 60).until(EC.url_changes(url))

def previous_pages(driver):
    '''test the previous buttons'''
    pages = [
        'Create',
        'Cluster Network',
        'Cluster',
        'Calico Nodes',
        'vCenter Details',
        'vCenter Login',
        'NDFC Fabric',
        'NDFC Login',
    ]
    for page in pages:
        click_previous(driver, assert_ndfc(driver, page))
    wait_for_title(driver,"Day0")
    
def main():
    chrome_options = Options()
    url = "http://localhost:5010"
    parser = argparse.ArgumentParser(description='pipeline testing script')
    parser.add_argument('--url', help='testing url')

    args, unknown = parser.parse_known_args()
    if args.url:
        url = args.url
    if unknown:
        chrome_driver_args = ' '.join(unknown)
        chrome_options.add_argument(chrome_driver_args)

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.get(url)

    root_page(driver)
    login_page(driver)
    fabric_page(driver)
    vcenter_login_page(driver)
    vcenter_page(driver)
    calico_node_page(driver)
    cluster_page(driver)
    cluster_network_page(driver)
    create_page(driver)
    previous_pages(driver)
    sleep(5)
    driver.quit()


if __name__ == "__main__":
    main()
