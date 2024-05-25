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

# Initialize WebDriver
driver = webdriver.Chrome()

try:
    # Monitor clipboard for specific data pattern
    data = monitor_clipboard()
    print(f"Detected data: {data}")

    # Open a new tab and navigate to the target URL
    driver.execute_script("window.open('https://pje.trt6.jus.br/', '_blank');")

    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[1])

    # Wait for the login button to be clickable and click it
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))
    ).click()

    # Wait for the input field to be present and fill it with the detected data
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "inputNumeroProcesso"))
    ).send_keys(data)

    # Click the button with the class name "mat-button-wrapper"
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "mat-button-wrapper"))
    ).click()

    # Perform additional steps if needed

finally:
    # Do not close the WebDriver, so the browser remains open
    pass
