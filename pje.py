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
        pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')
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
            
            # Construct the TRT URL dynamically
            trt_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual"
            
            # Construct the Astrea URL dynamically
            astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"
            
            # Open both TRT and Astrea tabs
            driver.execute_script(f"window.open('{trt_url}', '_blank');")
            driver.execute_script(f"window.open('{astrea_url}', '_blank');")
            
            # Switch to the TRT tab and perform actions
            driver.switch_to.window(driver.window_handles[-2])
            
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

            # Wait for the page to load after clicking the search button
            time.sleep(10)
            
            # Switch to the Astrea tab and perform actions
            driver.switch_to.window(driver.window_handles[-1])
            
            # Check if the login page is displayed by looking for the login element
            try:
                login_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "css-awdf6x-InputWrap"))
                )
                # Fill in the login credentials
                username_field = driver.find_element(By.NAME, "username")
                password_field = driver.find_element(By.NAME, "password")
                
                username_field.send_keys("xxx")
                password_field.send_keys("xxxx")
                
                # Submit the login form
                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                
                print("Logged in successfully.")
            except Exception as e:
                print("Login page not detected or error during login:", e)
                
            # Wait for the target button to be clickable and then click it
            try:
                button_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "css-dkul14-ButtonComponent"))
                )
                button_element.click()
                print("Button clicked successfully.")
            except Exception as e:
                print("Button not found or error during clicking:", e)

            time.sleep(10)  # Wait for a few seconds before checking the clipboard again
        time.sleep(1)  # Wait for a few seconds before checking the clipboard again

finally:
    driver.quit()  # Ensure the WebDriver is properly closed
