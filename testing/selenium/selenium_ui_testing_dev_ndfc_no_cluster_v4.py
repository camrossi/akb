from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import argparse
from time import sleep

def wait_for_title(driver, title):
    WebDriverWait(driver, 30).until(lambda x: title in x.title )

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
    elem = driver.find_element(By.ID,"deploy_vm-checkbox")
    elem.click()
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

def cluster_network_page(driver):
    wait_for_title(driver, "Cluster Network")
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    elem = driver.find_element(By.ID, "submit")
    current_url = driver.current_url
    elem.click()

    WebDriverWait(driver, 60).until(EC.url_changes(current_url))

def assert_ndfc(driver, title) -> str:
    '''Assert that ndfc fabric type is in the url with page title'''
    current_url = driver.current_url
    assert "fabric_type=vxlan_evpn" in current_url
    wait_for_title(driver,title)
    return current_url

def click_previous(driver, url):
    '''Click the previous button'''
    elem = driver.find_element(By.ID,'Previous')
    elem.click()

def main():
    chrome_options = Options()
    url = "http://localhost:5012"
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
    cluster_network_page(driver)
    sleep(5)
    #driver.quit()


if __name__ == "__main__":
    main()
