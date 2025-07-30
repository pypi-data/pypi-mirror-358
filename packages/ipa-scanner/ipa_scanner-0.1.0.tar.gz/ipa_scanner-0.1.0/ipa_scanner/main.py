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
    options.set_preference("browser.helperApps.neverAsk.saveToDisk",
        "application/octet-stream,application/pdf,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.add_argument("--width=1728")
    options.add_argument("--height=1021")

    driver = webdriver.Firefox(options=options)

    try:
        # Step 1: Open URL
        driver.get("https://ipa.wdf.sap.corp:8243/ipa?testgroup=ProcurementPlanningProject")
        time.sleep(3)

        # Step 2: Set window size
        driver.set_window_size(1728, 1021)

        # Step 3: Click user button
        driver.find_element(By.ID, "userButton-internalBtn-inner").click()
        time.sleep(1)

        # Step 4: Click logout
        driver.find_element(By.ID, "logoutBut-unifiedmenu-txt").click()
        time.sleep(1)

        # Step 5: Mouse over user button
        user_button = driver.find_element(By.ID, "userButton-internalBtn-inner")
        ActionChains(driver).move_to_element(user_button).perform()
        time.sleep(1)

        # Step 6: Click username input
        driver.find_element(By.ID, "__input32-__clone0-inner").click()
        time.sleep(0.5)

        # Step 7: Type username
        driver.find_element(By.ID, "__input32-__clone0-inner").send_keys(USERNAME)
        time.sleep(0.5)

        # Step 8: Click password input
        driver.find_element(By.ID, "__input34-inner").click()
        time.sleep(0.5)

        # Step 9: Type password
        driver.find_element(By.ID, "__input34-inner").send_keys(PASSWORD)
        time.sleep(0.5)

        # Step 10: Click login button
        driver.find_element(By.ID, "__button77-BDI-content").click()
        time.sleep(3)

        ########################

        # Step 12: Click scenario-reset
        driver.find_element(By.ID, "scenario-reset").click()
        time.sleep(1)

        # Step 13: Click scenario-search
        driver.find_element(By.ID, "scenario-search").click()
        time.sleep(2)

        # Step 14: Click item48
        driver.find_element(By.ID, "__item48").click()
        time.sleep(1)

        # Step 15: Click stepMode-arrow
        driver.find_element(By.ID, "stepMode-arrow").click()
        time.sleep(1)

        # Step 16: Click __item4
        driver.find_element(By.ID, "__item4").click()
        time.sleep(1)

        # Step 17: Click dispMode-arrow
        driver.find_element(By.ID, "dispMode-arrow").click()
        time.sleep(1)

        # Step 18: Click __item0
        driver.find_element(By.ID, "__item0").click()
        time.sleep(1)

        # Step 19: Click __button38-img (likely download or next action)
        driver.find_element(By.ID, "__button38-img").click()
        time.sleep(3)

        # Optional: list downloaded files
        downloaded_files = os.listdir(download_dir)
        print("Downloaded files:", downloaded_files)
        return download_dir
    finally:
        driver.quit()

def cli_entrypoint():
    print("== IPA Scanner Login ==")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    run_bom_download(username, password)
