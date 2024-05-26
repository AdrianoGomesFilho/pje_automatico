import time
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to monitor clipboard and detect specific pattern
def monitor_clipboard():
    pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4}')
    last_paste = ""
    
    while True:
        paste = pyperclip.paste()
        if paste != last_paste and pattern.match(paste):
            return paste
        last_paste = paste
        time.sleep(1)

# Specify the path to your Chrome user data directory
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(r"--user-data-dir=C:\Users\fish\AppData\Local\Google\Chrome\User Data\Adriano")

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

try:
    # Monitor clipboard for specific data pattern
    data = monitor_clipboard()
    print(f"Detected data: {data}")

    # Open a new tab and navigate to the target URL
    driver.execute_script("window.open('https://pje.trt6.jus.br/consultaprocessual', '_blank');")

    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[-1])

    # Wait for the input field to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nrProcessoField")))

    # Enter the detected data into the input field
    input_field = driver.find_element(By.CLASS_NAME, "mat-input-element")
    input_field.send_keys(data)

    # Wait for the search button to be clickable and then click it
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnPesquisar"))
    )
    search_button.click()

finally:
    time.sleep(200)  # Wait for a few seconds to observe the results
    driver.quit()  # Ensure the WebDriver is properly closed
