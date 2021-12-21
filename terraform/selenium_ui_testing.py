from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
def add_anchor_ndoe(pod_id,rack_id,node_id,rtr_id,node_ipv4,node_ipv6):
    elem = driver.find_element(By.NAME,"pod_id")
    elem.send_keys(pod_id)
    elem = driver.find_element(By.NAME,"rack_id")
    elem.clear()
    elem.send_keys(rack_id)
    select = Select(driver.find_element(By.ID,'node_id'))
    select.select_by_visible_text(node_id)
    elem = driver.find_element(By.NAME,"rtr_id")
    elem.clear()
    elem.send_keys(rtr_id)
    elem = driver.find_element(By.NAME,"node_ipv4")
    elem.clear()
    elem.send_keys(node_ipv4)
    elem = driver.find_element(By.NAME,"node_ipv6")
    elem.clear()
    elem.send_keys(node_ipv6)
    elem = driver.find_element(By.ID,"add_node")
    elem.click()

def add_calico_ndoe(hostname, ip, ipv6, local_as, rack_id):
    elem = driver.find_element(By.NAME,"hostname")
    elem.clear()
    elem.send_keys(hostname)
    elem = driver.find_element(By.NAME,"ip")
    elem.clear()
    elem.send_keys(ip)
    elem = driver.find_element(By.NAME,"ipv6")
    elem.clear()
    elem.send_keys(ipv6)
    elem = driver.find_element(By.NAME,"local_as")
    elem.clear()
    elem.send_keys(local_as)
    elem = driver.find_element(By.NAME,"rack_id")
    elem.clear()
    elem.send_keys(rack_id)
    elem = driver.find_element(By.ID,"add_node")
    elem.click()

driver = webdriver.Chrome()

driver.get("http://10.67.185.120:5002/")
assert "AKB" in driver.title

current_url = driver.current_url
elem = driver.find_element(By.NAME,"button")
elem.click()
#Wait for the page to be loaded
WebDriverWait(driver, 15).until(EC.url_changes(current_url))

assert "Apic Login" in driver.title
elem = driver.find_element(By.NAME,"fabric")
elem.send_keys("10.67.185.102")
elem = driver.find_element(By.NAME,"username")
elem.send_keys("ansible")
elem = driver.find_element(By.NAME,"certname")
elem.send_keys("ansible.crt")
elem = driver.find_element(By.NAME,"privatekey")
elem.send_keys("/home/cisco/Coding/ansible.key")
elem = driver.find_element(By.ID,"submit")
current_url = driver.current_url
elem.click()
#Wait for the page to be loaded
WebDriverWait(driver, 15).until(EC.url_changes(current_url))

assert "L3OUT" in driver.title
elem = driver.find_element(By.ID,'l3out_tenant')
elem.send_keys("calico2")
elem = driver.find_element(By.ID,'name')
elem.clear()
elem.send_keys("calico_l3out")

# WAIT FOR THE vrf_name_list TO BE POPULATED WITH AT LEAST 2 ELEMENTs (The first one is just the palce holder)
# THAT SHOULD BE ALL IT TAKES TO HAVE THE REST OF THE PAGE READY...
try:
    elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="vrf_name_list"]/option[2]')))
except ValueError as e:
    print("Loading took too much time!")

elem = driver.find_element(By.ID,'vrf_name')
elem.send_keys("calico2/vrf")
elem = driver.find_element(By.ID,'contract')
elem.send_keys("common/calico2")
elem = driver.find_element(By.ID,'physical_dom')
elem.send_keys("Fab2")

elem = driver.find_element(By.ID,'mtu')
elem.clear()
elem.send_keys("9000")

elem = driver.find_element(By.NAME,"ipv4_cluster_subnet")
elem.send_keys("192.168.12.0/24")
elem = driver.find_element(By.NAME,"ipv6_cluster_subnet")
elem.send_keys("2001:db8:12::0/56")
#elem = driver.find_element(By.NAME,"vlan_id")
#elem.send_keys("310")
elem = driver.find_element(By.NAME,"dns_servers")
elem.send_keys("10.67.185.100")
elem = driver.find_element(By.NAME,"dns_domain")
elem.send_keys("cam.ciscolabs.com")

elem = driver.find_element(By.ID,"import-security-checkbox")
elem.click()
elem = driver.find_element(By.ID,"shared-security-checkbox")
elem.click()
elem = driver.find_element(By.ID,"shared-rtctrl-checkbox")
elem.click()

add_anchor_ndoe("1","1","201","1.1.1.201","192.168.12.201","2001:db8:12::201/56")
add_anchor_ndoe("1","1","202","1.1.1.202","192.168.12.202/24","2001:db8:12::202/56")
add_anchor_ndoe("1","2","203","1.1.1.203","192.168.12.203/24","2001:db8:12::203/56")
add_anchor_ndoe("1","2","204","1.1.1.204","192.168.12.204/24","2001:db8:12::204/56")
current_url = driver.current_url

elem = driver.find_element(By.ID,"submit")
elem.click()

#Wait for the page to be loaded
WebDriverWait(driver, 15).until(EC.url_changes(current_url))

assert "vCenter Login" in driver.title
elem = driver.find_element(By.NAME,"url")
elem.send_keys("vc2.cam.ciscolabs.com")
elem = driver.find_element(By.NAME,"username")
elem.send_keys("administrator@vsphere.local")
elem = driver.find_element(By.NAME,"pass")
elem.send_keys("123Cisco123!")
elem = driver.find_element(By.ID,"submit")
current_url = driver.current_url
elem.click()

#Wait for the page to be loaded
WebDriverWait(driver, 15).until(EC.url_changes(current_url))
assert "vCenter Details" in driver.title
select = Select(driver.find_element(By.ID,'dc'))
select.select_by_visible_text("STLD")

#Wait for vCenter API to populate the page
try:
    elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="datastore_list"]/option[1]')))
except ValueError as e:
    print("Loading took too much time!")

elem = driver.find_element(By.ID,'datastore')
elem.send_keys("BM01")
select = Select(driver.find_element(By.ID,'cluster'))
select.select_by_visible_text("Cluster")
elem = driver.find_element(By.ID,'port_group')
elem.send_keys("ACI/CalicoL3OUT-310/vlan-310")
elem = driver.find_element(By.ID,'vm_templates')
elem.send_keys("Ubuntu21-Template")
elem = driver.find_element(By.ID,'vm_folder')
elem.send_keys("Calico-Cluster2")
elem = driver.find_element(By.ID,"submit")
current_url = driver.current_url
elem.click()

#Wait for the page to be loaded
WebDriverWait(driver, 15).until(EC.url_changes(current_url))
assert "Calico Nodes" in driver.title
add_calico_ndoe('calico-1','192.168.12.11/24','2001:db8:12::11/56', '11', '1')
add_calico_ndoe('calico-2','192.168.12.12/24','2001:db8:12::12/56', '12', '1')
add_calico_ndoe('calico-3','192.168.12.13/24','2001:db8:12::13/56', '13', '2')
add_calico_ndoe('calico-4','192.168.12.14/24','2001:db8:12::14/56', '14', '2')

elem = driver.find_element(By.ID,"submit")
current_url = driver.current_url
elem.click()

#Wait for the page to be loaded
WebDriverWait(driver, 15).until(EC.url_changes(current_url))
assert "Cluster" in driver.title
elem = driver.find_element(By.ID,'kube_version')
elem.send_keys("1.22.4-00")
elem = driver.find_element(By.ID,'crio_os')
elem.send_keys("xUbuntu_20.04")
elem = driver.find_element(By.ID,'timezone')
elem.send_keys("Australia/Sydney")
elem = driver.find_element(By.ID,'docker_mirror')
elem.send_keys("10.67.185.120:5000")
elem = driver.find_element(By.ID,'ntp_server')
elem.send_keys("72.163.32.44")
elem = driver.find_element(By.ID,"submit")
current_url = driver.current_url
elem.click()
WebDriverWait(driver, 15).until(EC.url_changes(current_url))
driver.exit()