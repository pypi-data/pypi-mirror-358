from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
import time
import os
import getpass
def run_bom_download(username, password):
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    options = Options()
    options.headless = True
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "application/octet-stream,application/pdf,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    options.set_preference("pdfjs.disabled", True)
    options.add_argument("--headless")
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.add_argument("--width=1728")
    options.add_argument("--height=1021")

    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://ipa.wdf.sap.corp:8243/ipa?testgroup=ProcurementPlanningProject")
        time.sleep(3)
        driver.set_window_size(1728, 1021)

        driver.find_element(By.ID, "userButton-internalBtn-inner").click()
        time.sleep(1)
        driver.find_element(By.ID, "logoutBut-unifiedmenu-txt").click()
        time.sleep(1)

        ActionChains(driver).move_to_element(
            driver.find_element(By.ID, "userButton-internalBtn-inner")
        ).perform()
        time.sleep(1)

        driver.find_element(By.ID, "__input32-__clone0-inner").click()
        driver.find_element(By.ID, "__input32-__clone0-inner").send_keys(username)
        driver.find_element(By.ID, "__input34-inner").click()
        driver.find_element(By.ID, "__input34-inner").send_keys(password)
        driver.find_element(By.ID, "__button77-BDI-content").click()
        time.sleep(3)

        driver.find_element(By.ID, "scenario-reset").click()
        time.sleep(1)
        driver.find_element(By.ID, "scenario-search").click()
        time.sleep(2)
        driver.find_element(By.ID, "__item48").click()
        time.sleep(1)
        driver.find_element(By.ID, "stepMode-arrow").click()
        time.sleep(1)
        driver.find_element(By.ID, "__item4").click()
        time.sleep(1)
        driver.find_element(By.ID, "dispMode-arrow").click()
        time.sleep(1)
        driver.find_element(By.ID, "__item0").click()
        time.sleep(1)
        driver.find_element(By.ID, "__button38-img").click()
        time.sleep(3)

        print("Downloaded files:", os.listdir(download_dir))
        return download_dir
    finally:
        driver.quit()

def cli_entrypoint():
    print("== IPA Scanner Login ==")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    run_bom_download(username, password)


