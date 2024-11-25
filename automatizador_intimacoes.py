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
import json

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

# Load URLs from urls.txt
with open('/c:/Users/fish/script_pje/urls.txt', 'r', encoding='utf-8') as file:
    urls_data = json.load(file)

# Store the last clipboard content
last_clipboard_content = ""

def find_or_open_tab(driver, base_url):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if base_url in driver.current_url:
            return handle
    # If the tab is not found, open a new one
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    new_handle = driver.window_handles[-1]
    return new_handle

def get_base_url(judicial_branch, tribunal_code):
    if judicial_branch == '5':  # Justiça do Trabalho
        return urls_data["Justiça do Trabalho"].get(f"TRT {tribunal_code}ª Região")
    elif judicial_branch == '4':  # Justiça Federal
        return urls_data["Justiça Federal"].get(f"TRF {tribunal_code}ª Região", {}).get("1º grau")
    elif judicial_branch == '8':  # Justiça Comum
        for state_abbr, tribunals in urls_data["Justiça Comum"].items():
            if f"TJ{state_abbr}" in tribunals:
                return tribunals[f"TJ{state_abbr}"]
    return None

try:
    while True:
        # Monitor clipboard for specific data pattern
        pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')
        paste = pyperclip.paste()

        # Check if the clipboard content is new and matches the pattern
        if paste != last_clipboard_content and pattern.match(paste):
            print(f"Processo identificado: {paste}")

            # Update the last clipboard content
            last_clipboard_content = paste

            # Extract the judicial branch and tribunal code
            judicial_branch = paste[16]
            tribunal_code = paste[18:20].lstrip('0')

            # Construct the base URL dynamically
            base_url = get_base_url(judicial_branch, tribunal_code)
            if base_url:
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
                WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.ID, button_id))).click()

                # Wait for the "loginAplicacaoButton" button to be clickable and click it
                WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()
                
                # Wait for login to complete before proceeding
                WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "nome-usuario")))
                print(f"Login realizado (token)")

                final_url = f"{base_url}/consultaprocessual/detalhe-processo/{paste}"
                
                # Open the final URL in a new tab
                driver.execute_script(f"window.open('{final_url}', '_blank');")

                # Close the base_url tab
                driver.close()

                # Switch back to the original tab
                driver.switch_to.window(driver.window_handles[0])

                #########################ASTREA######################################

                # Construct the Astrea URL dynamically
                astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"

                # Find or open the tab for astrea_url
                astrea_handle = find_or_open_tab(driver, astrea_url)
                driver.switch_to.window(astrea_handle)

                # Login to Astrea if necessary
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
