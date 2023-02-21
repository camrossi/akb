from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
from time import sleep
from selenium_utils import wait_for_clickable

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
    wait_for_clickable(driver,(By.ID,"add_node"))

    
def wait_for_title(driver, title):
    WebDriverWait(driver, 30).until(lambda x: title in x.title )

chrome_options = Options()
if len(sys.argv)>=2:
    port= sys.argv[1]
    chrome_options.add_argument(sys.argv[1])
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)

driver.get("http://10.67.185.120:5006")
assert "NKT" in driver.title
elem = driver.find_element(By.NAME,"button")
elem.click()
wait_for_title(driver, "Apic Login")
elem = driver.find_element(By.ID,"deploy_vm-checkbox")
elem.click()
elem = driver.find_element(By.NAME,"fabric")
elem.clear()
elem.send_keys("fab2-apic1.cam.ciscolabs.com")
elem = driver.find_element(By.NAME,"username")
elem.clear()
elem.send_keys("admin")
elem = driver.find_element(By.NAME,"password")
elem.clear()
elem.send_keys("123Cisco123")
elem = driver.find_element(By.ID,"submit")
elem.click()
#Wait for the page to be loaded
wait_for_title(driver, "L3OUT")

elem = driver.find_element(By.ID,'l3out_tenant')
elem.send_keys("Cilium")
elem = driver.find_element(By.NAME,"ipv4_cluster_subnet")
elem.clear()
elem.send_keys("192.168.11.0/24")
# WAIT FOR THE vrf_name_list TO BE POPULATED WITH AT LEAST 2 ELEMENTs (The first one is just the palce holder)
# THAT SHOULD BE ALL IT TAKES TO HAVE THE REST OF THE PAGE READY...
try:
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="vrf_name_list"]/option[2]')))
except ValueError as e:
    print("Loading took too much time!")

elem = driver.find_element(By.ID,'vrf_name')
elem.send_keys("Cilium/Cilium")
elem = driver.find_element(By.ID,'contract')
elem.send_keys("common/cilium_permit_all")
elem = driver.find_element(By.ID,'physical_dom')
elem.send_keys("Fab2")

add_anchor_node("1","1","201","1.1.1.101","192.168.11.101")
add_anchor_node("1","1","202","1.1.1.102","192.168.11.102/24")
add_anchor_node("1","2","203","1.1.1.103","192.168.11.103")
add_anchor_node("1","2","204","1.1.1.104","192.168.11.104/24")

elem = driver.find_element(By.ID,"submit")
elem.click()

wait_for_title(driver, "Cluster Network")
elem = driver.find_element(By.ID,'cni_plugin')
elem.clear()
elem.send_keys("Cilium")
elem = driver.find_element(By.ID,"vlan_id")
elem.send_keys("11")
elem = driver.find_element(By.ID,"submit")

elem.click()
wait_for_title(driver, "Create")
driver.quit()