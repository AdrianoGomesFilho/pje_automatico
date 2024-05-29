import time
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Specify the path to your Chrome user data directory
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing

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
            
            # Construct the base URL dynamically
            base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
            
            # Open a new tab and navigate to the base URL
            driver.execute_script(f"window.open('{base_url}', '_blank');")

            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])

            # Wait for the "modo-operacao" button to be clickable and click it
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "modo-operacao"))).click()
            
            try:
                # Wait for the "j_id112:btnUtilizarPjeOffice" button to be clickable and click it
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_id111:btnUtilizarPjeOffice"))).click()
            except TimeoutException:
                # If the first ID is not present, select the alternative ID
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_id112:btnUtilizarPjeOffice"))).click()

            # Wait for the "loginAplicacaoButton" button to be clickable and click it
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()
            
            # Wait up to 8 seconds for the page to load after handling the pop-up, but proceed as soon as the element is found
            WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CLASS_NAME, "nome-usuario")))  # Replace "desired_element_id_after_login" with the actual element ID you expect to be loaded after login
            
            # Construct the final URL with the specific data pattern appended
            final_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"

            # Store the handle of the current tab before opening the new tab
            current_tab_handle = driver.current_window_handle

            # Open a new tab and navigate to the final URL
            driver.execute_script(f"window.open('{final_url}', '_blank');")

            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])

            # Close the previous tab
            driver.switch_to.window(current_tab_handle)
            driver.close()

            # Switch back to the new tab
            driver.switch_to.window(driver.window_handles[-1])

        time.sleep(1)  # Wait before checking the clipboard again

except Exception as e:
    print(f"An error occurred: {e}")
