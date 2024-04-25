from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import seleniumwire.undetected_chromedriver.v2 as uc
import time
import json

options = ChromeOptions()
options.add_argument("--ignore-certificate-errors")

driver = uc.Chrome(options=options)

driver.set_script_timeout(120)
driver.get("https://cars.ksl.com")

driver.execute_cdp_cmd("Network.enable", {})

find_a_car = WebDriverWait(driver, 100).until(
    EC.presence_of_element_located((By.CLASS_NAME, "find-a-car"))
)


make_dropdown = find_a_car.find_element(
    By.CLASS_NAME, "form-line.makes.dropdown-wrapper"
)

model_dropdown = find_a_car.find_element(
    By.CLASS_NAME, "form-line.models.dropdown-wrapper"
)


def click_model_dropdown():
    ActionChains(driver).move_to_element(model_dropdown).click(model_dropdown).perform()


def click_make_dropdown():
    ActionChains(driver).move_to_element(make_dropdown).click(make_dropdown).perform()


model_checkbox_script = """
var checkboxes = document.querySelectorAll('.option-list.zip-radius div li label input[type="checkbox"]')

checkboxes.forEach(function(checkbox) {
    if(!checkbox.checked) {
        checkbox.click();
    }
});
"""


def get_trim_jsons():
    time.sleep(1)
    click_make_dropdown()
    time.sleep(1)
    make_list = make_dropdown.find_element(By.CLASS_NAME, "option-list.makes")
    make_list_items = make_list.find_elements(By.TAG_NAME, "li")
    for li in make_list_items:
        label = li.find_element(By.TAG_NAME, "label")
        checkbox = label.find_element(By.TAG_NAME, "input")
        span = label.find_element(By.TAG_NAME, "span")
        name = span.text
        ActionChains(driver).move_to_element(checkbox).click(checkbox).perform()
        click_make_dropdown()
        time.sleep(4)
        click_model_dropdown()
        driver.execute_script(model_checkbox_script)
        time.sleep(5)
        if driver.requests[-1].response is not None:
            print(driver.requests[-1].url)
            print(driver.requests[-1].response.headers["Content-Type"])
            response = driver.requests[-1].response.body.decode("utf-8")
            response_json = json.loads(response)
            with open(name + ".json", "w", encoding="utf-8") as file:
                json.dump(response_json, file, indent=4)
        time.sleep(5)
        click_model_dropdown()
        click_make_dropdown()
        ActionChains(driver).move_to_element(checkbox).click(checkbox).perform()
        time.sleep(2)


get_trim_jsons()


time.sleep(12)


driver.quit()
