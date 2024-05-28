import time
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Specify the path to your Chrome user data directory
chrome_options = webdriver.ChromeOptions()

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Store the last clipboard content
last_clipboard_content = ""

try:
    while True:
        # Monitor clipboard for specific data pattern
        pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4}')
        paste = pyperclip.paste()

        # Check if the clipboard content is new and matches the pattern
        if paste != last_clipboard_content and pattern.match(paste):
            print(f"Detected data: {paste}")
            
            # Update the last clipboard content
            last_clipboard_content = paste
            
            # Extract the TRT number (15th and 16th characters)
            trt_number = paste[18:20]
            
            # Remove leading zero if present
            trt_number = trt_number.lstrip('0')
            
            # Construct the URL dynamically
            url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual"
            
            # Open a new tab and navigate to the target URL
            driver.execute_script(f"window.open('{url}', '_blank');")

            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])

            # Wait for the input field to be present
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nrProcessoField")))

            # Enter the detected data into the input field
            input_field = driver.find_element(By.CLASS_NAME, "mat-input-element")
            input_field.send_keys(paste)

            # Wait for the search button to be clickable and then click it
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnPesquisar"))
            )
            search_button.click()

            time.sleep(5)  # Wait for a few seconds before checking the clipboard again

        time.sleep(1)  # Wait before checking the clipboard again

finally:
    driver.quit()  # Ensure the WebDriver is properly closed
