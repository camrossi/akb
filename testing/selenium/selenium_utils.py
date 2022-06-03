from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_clickable(driver, ref):
    c = 0
    while c < 30:
        try:
            c = c + 1
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(ref))
            break
        except Exception:
            continue