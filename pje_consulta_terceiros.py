import time
import re
from threading import Thread
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from dotenv import load_dotenv

# Specify the path to your external .env file like this load_dotenv('credenciais.env')
load_dotenv('credenciais.env')
print("Loaded .env file")

# Get credentials from environment variables
usuario = os.getenv("USERNAMEASTREA")
senha = os.getenv("PASSWORDASTREA")
print(f"Username: {usuario}")
print(f"Password: xxxxxxxxxxxx")

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
            print(f"Processo identificado: {paste}")
            
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

            # Wait for the "modo-operacao" element to be present
            modo_operacao_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modo-operacao")))
            modo_operacao_element.click()
            buttons = driver.find_elements(By.XPATH, "//*[contains(@id, 'UtilizarPjeOffice')]")
            button_id = buttons[0].get_attribute('id')
            button_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, button_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, button_id))).click()

            # Wait for the "loginAplicacaoButton" button to be clickable and click it
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "nome-usuario")))
            
            final_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"

            # Open the final URL in a new tab
            driver.execute_script(f"window.open('{final_url}', '_blank');")

            # Close the base_url tab
            driver.close()

            # Switch back to the original tab
            driver.switch_to.window(driver.window_handles[0])
            
            #########################ASTREA######################################
            
            # Construct the Astrea URL dynamically
            astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"

            # Store the handle of the Astrea URL tab
            astrea_tab_handle = driver.current_window_handle

            # Open the Astrea URL in a new tab
            driver.execute_script(f"window.open('{astrea_url}', '_blank');")

            # Switch to the Astrea URL tab
            driver.switch_to.window(driver.window_handles[-1])

            # Login to Astrea
            try:
                login_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                
                # Credentials
                username_field = driver.find_element(By.NAME, "username")
                password_field = driver.find_element(By.NAME, "password")
                
                username_field.send_keys(usuario)
                password_field.send_keys(senha)
                
                # Submit the login form
                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                
                print("Logged in to Astrea successfully.")
            except Exception as e:
                print("Login page not detected or error during login:", e)


        time.sleep(1)  # Wait before checking the clipboard again

except Exception as e:
    print(f"An error occurred: {e}")

