from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
from time import sleep

def wait_for_title(driver, title):
    WebDriverWait(driver, 30).until(lambda x: title in x.title )

def add_anchor_node(pod_id,rack_id,node_id,rtr_id,node_ipv4):
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
    elem = driver.find_element(By.ID,"add_node")
    elem.click()
    sleep(1)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID,"add_node")))
    

def add_calico_ndoe(hostname, ip, natip, rack_id):
    elem = driver.find_element(By.NAME,"hostname")
    elem.clear()
    elem.send_keys(hostname)
    elem = driver.find_element(By.NAME,"ip")
    elem.clear()
    elem.send_keys(ip)
    elem = driver.find_element(By.NAME,"natip")
    elem.clear()
    elem.send_keys(natip)
    elem = driver.find_element(By.NAME,"rack_id")
    elem.clear()
    elem.send_keys(rack_id)
    elem = driver.find_element(By.ID,"add_node")
    elem.click()
    sleep(1)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID,"add_node")))
    

chrome_options = Options()
if len(sys.argv)>=2:
    port= sys.argv[1]
    chrome_options.add_argument(sys.argv[1])
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)

driver.get("http://10.48.168.169:5005")
wait_for_title(driver, "NKT")
elem = driver.find_element(By.NAME,"button")
elem.click()

wait_for_title(driver, "Apic Login")

elem = driver.find_element(By.NAME,"fabric")
elem.clear()
elem.send_keys("https://10.48.170.201")
elem = driver.find_element(By.NAME,"username")
elem.clear()
elem.send_keys("admin")
elem = driver.find_element(By.NAME,"password")
elem.clear()
elem.send_keys("ins3965!")
elem = driver.find_element(By.ID,"submit")
elem.click()

wait_for_title(driver, "L3OUT")

elem = driver.find_element(By.ID,'l3out_tenant')
elem.send_keys("common")
elem = driver.find_element(By.NAME,"ipv4_cluster_subnet")
elem.clear()
elem.send_keys("192.168.20.0/24")
# WAIT FOR THE vrf_name_list TO BE POPULATED WITH AT LEAST 2 ELEMENTs (The first one is just the palce holder)
# THAT SHOULD BE ALL IT TAKES TO HAVE THE REST OF THE PAGE READY...
try:
   WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="vrf_name_list"]/option[2]')))
except ValueError as e:
    print("Loading took too much time!")

elem = driver.find_element(By.ID,'vrf_name')
elem.send_keys("common/k8sVRF2")
elem = driver.find_element(By.ID,'contract')
elem.send_keys("common/k8s")
elem = driver.find_element(By.ID,'physical_dom')
elem.send_keys("k8slab-pdom")

add_anchor_node("1","1","101","1.1.1.1","192.168.20.101/24")
add_anchor_node("1","1","102","1.1.1.2","192.168.20.102/24")

elem = driver.find_element(By.ID,"submit")
elem.click()

wait_for_title(driver, "vCenter Login")

elem = driver.find_element(By.NAME,"url")
elem.send_keys("10.48.170.23")
elem = driver.find_element(By.NAME,"username")
elem.send_keys("administrator@dom.local")
elem = driver.find_element(By.NAME,"pass")
elem.send_keys("C!sc0123")
elem = driver.find_element(By.ID,"template_checkbox")
elem.click()
elem = driver.find_element(By.ID,"submit")

elem.click()
wait_for_title(driver, "vCenter Details")

select = Select(driver.find_element(By.ID,'dc'))
select.select_by_visible_text("DC1")

#Wait for vCenter API to populate the page
try:
    WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.XPATH, '//*[@id="vms_list"]/option[1]')))
except ValueError as e:
    print("Loading took too much time!")
#elem = driver.find_element(By.ID,'datastore')
#elem.send_keys("ESXi3_SSD")
select = Select(driver.find_element(By.ID,'cluster'))
select.select_by_visible_text("Compute")
elem = driver.find_element(By.ID,'port_group')
elem.send_keys("vc02-DC1/vlan_k8s1/vlan-771")
elem = driver.find_element(By.ID,'vm_templates')
elem.send_keys("nkt_template")
elem = driver.find_element(By.ID,'vm_folder')
elem.send_keys("CiscoLive")
elem = driver.find_element(By.ID,"submit")
elem.click()

wait_for_title(driver, "Calico Nodes")

elem = driver.find_element(By.ID,'calico_nodes')
elem.clear()
add_calico_ndoe('gitaction-nkt-master-1','192.168.20.1/24', "10.48.170.130",'1')
add_calico_ndoe('gitaction-nkt-master-2','192.168.20.2/24', "10.48.170.131",'1')
add_calico_ndoe('gitaction-nkt-master-3','192.168.20.3/24', "10.48.170.132",'1')



elem = driver.find_element(By.ID,"submit")
elem.click()

wait_for_title(driver, "Cluster")

elem = driver.find_element(By.ID,'advanced')
elem.click()
elem = driver.find_element(By.ID,'timezone')
elem.send_keys("Europe/Rome")
elem = driver.find_element(By.NAME,"dns_servers")
elem.send_keys("10.48.170.50")
elem = driver.find_element(By.NAME,"dns_domain")
elem.send_keys("k8s.cisco.com")
elem = driver.find_element(By.ID,'ntp_server')
elem.send_keys("72.163.32.44")
elem = driver.find_element(By.ID,"submit")
elem.click()
wait_for_title(driver, "Cluster Network")
elem = driver.find_element(By.ID,"submit")
elem.click()
wait_for_title(driver, "Create")
driver.quit()