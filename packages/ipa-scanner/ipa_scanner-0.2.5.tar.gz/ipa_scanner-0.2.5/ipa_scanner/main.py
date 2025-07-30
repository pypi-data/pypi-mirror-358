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
    # options.headless = True
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "application/octet-stream,application/pdf,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    options.set_preference("pdfjs.disabled", True)
    # options.add_argument("--headless")
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.add_argument("--width=1728")
    options.add_argument("--height=1021")

    driver = webdriver.Firefox(options=options)

    try:
        # Open URL and set window
        driver.get("https://ipa.wdf.sap.corp:8243/ipa?testgroup=ProcurementPlanningProject")
        time.sleep(3)
        driver.set_window_size(1728, 1021)

        # Login process
        driver.find_element(By.ID, "userButton-internalBtn-content").click()
        time.sleep(1)

        driver.find_element(By.ID, "logoutBut-unifiedmenu").click()
        time.sleep(1)

        driver.find_element(By.ID, "__input32-__clone0-inner").click()
        time.sleep(0.5)
        driver.find_element(By.ID, "__input32-__clone0-inner").send_keys(username)

        driver.find_element(By.ID, "__input34-inner").click()
        time.sleep(0.5)
        driver.find_element(By.ID, "__input34-inner").send_keys(password)

        driver.find_element(By.ID, "__button77-BDI-content").click()
        time.sleep(3)

        # Set step mode and display mode once
        driver.find_element(By.ID, "stepMode-arrow").click()
        time.sleep(1)
        driver.find_element(By.ID, "__item4").click()
        time.sleep(1)
        driver.find_element(By.ID, "dispMode-arrow").click()
        time.sleep(1)
        driver.find_element(By.ID, "__item0").click()
        time.sleep(1)

        # Item list to process
        item_ids = ["__item48", "__item59", "__item70", "__item81", "__item92", "__item103", "__item114"]

        for item_id in item_ids:
            try:
                # Reset and search
                driver.find_element(By.ID, "scenario-reset").click()
                time.sleep(1)
                driver.find_element(By.ID, "scenario-search").click()
                time.sleep(2)

                # Select item and download
                driver.find_element(By.ID, item_id).click()
                time.sleep(1)
                driver.find_element(By.ID, "__button38-img").click()
                time.sleep(3)

            except Exception as e:
                print(f"⚠️ Skipping {item_id} due to error: {e}")

        # Logout
        driver.find_element(By.ID, "userButton-internalBtn-inner").click()
        time.sleep(1)
        driver.find_element(By.ID, "logoutBut-unifiedmenu").click()
        time.sleep(1)

        # Show downloaded files
        files = os.listdir(download_dir)
        print("✅ Downloaded files:", files)
        return download_dir

    finally:
        driver.quit()

def cli_entrypoint():
    print("== IPA Scanner Login ==")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    run_bom_download(username, password)

# if __name__ == "__main__":
#     cli_entrypoint()
