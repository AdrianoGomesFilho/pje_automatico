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

# Load credentials from .env file
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
chrome_options.add_argument("--start-maximized")  # Open browser in fullscreen

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Store the last clipboard content
last_clipboard_content = ""

def find_or_open_tab(driver, base_url, data_url=None):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if base_url in driver.current_url or (data_url and data_url in driver.current_url):
            return handle
    # Switch to the last tab before opening a new one
    driver.switch_to.window(driver.window_handles[-1])
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    new_handle = driver.window_handles[-1]
    return new_handle

try:
    while True:
        # Monitor clipboard for specific data pattern
        pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')
        paste = pyperclip.paste()

        # Check if the clipboard content is new and matches the pattern
        if paste != last_clipboard_content and pattern.match(paste):
            print(f"Processo identificado: {paste}")
            last_clipboard_content = paste  # Update the last clipboard content

            #########################ASTREA######################################

            # Perform Astrea login and other actions
            astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"
            driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
            driver.execute_script(f"window.open('{astrea_url}', '_blank');")
            astrea_handle = driver.window_handles[-1]
            driver.switch_to.window(astrea_handle)

            logged_in = False

            if not logged_in:
                try:
                    # Check if the login element is present
                    login_element = WebDriverWait(driver, 2).until(
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
                    logged_in = True
                except:
                    print("Already logged in to Astrea or login page not detected.")
            else:
                print("Skipping login as already logged in.")

            #########################PJE######################################

            # Construct the base URL dynamically
            base_url = f"https://pje.tst.jus.br/tst/login.seam"

            # Find or open the tab for base_url
            base_url_handle = find_or_open_tab(driver, base_url)
            driver.switch_to.window(base_url_handle)

            # Wait for the "modo-operacao" element to be present
            modo_operacao_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modo-operacao")))
            modo_operacao_element.click()
            buttons = driver.find_elements(By.XPATH, "//*[contains(@id, 'UtilizarPjeOffice')]")
            button_id = buttons[0].get_attribute('id')
            button_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, button_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, button_id))).click()

            # Wait for the "loginAplicacaoButton" button to be clickable and click it
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()

            # Wait for login to complete before proceeding
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "nome-usuario")))
            print(f"Login realizado (token)")

            final_url = f"https://pje.tst.jus.br/consultaprocessual/detalhe-processo/{paste}"

            # Open the final URL in a new tab and close the base URL tab
            driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
            driver.execute_script(f"window.open('{final_url}', '_blank');")
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])

        time.sleep(1)  # Wait before checking the clipboard again

except Exception as e:
    print(f"An error occurred: {e}")