import time
import re
from concurrent.futures import ThreadPoolExecutor
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def find_or_open_tab(driver, base_url):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if base_url in driver.current_url:
            return handle
    # If the tab is not found, open a new one
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    new_handle = driver.window_handles[-1]
    return new_handle

def open_pje_tab(trt_number, paste):
    try:
        base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
        base_url_handle = find_or_open_tab(driver, base_url)
        driver.switch_to.window(base_url_handle)

        # Wait for the "modo-operacao" element to be present
        modo_operacao_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modo-operacao"))
        )
        modo_operacao_element.click()
        buttons = driver.find_elements(By.XPATH, "//*[contains(@id, 'UtilizarPjeOffice')]")
        button_id = buttons[0].get_attribute('id')
        button_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, button_id))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, button_id))).click()

        # Wait for the "loginAplicacaoButton" button to be clickable and click it
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))
        ).click()

        # Wait for login to complete before proceeding
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nome-usuario"))
        )
        print(f"Login realizado (token)")

        final_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"
        driver.execute_script(f"window.open('{final_url}', '_blank');")
    except Exception as e:
        print(f"Error during PJE process: {e}")

def open_astrea_tab(paste):
    try:
        astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"
        astrea_handle = find_or_open_tab(driver, astrea_url)
        driver.switch_to.window(astrea_handle)

        # Login to Astrea if necessary
        try:
            login_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )

            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")

            username_field.send_keys(usuario)
            password_field.send_keys(senha)

            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            print("Logged in to Astrea successfully.")
        except Exception as e:
            print("Login page not detected or error during login:", e)
    except Exception as e:
        print(f"Error during Astrea process: {e}")

try:
    while True:
        pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')
        paste = pyperclip.paste()

        if paste != last_clipboard_content and pattern.match(paste):
            print(f"Processo identificado: {paste}")
            last_clipboard_content = paste

            trt_number = paste[18:20].lstrip('0')

            # Open PJE and Astrea tabs asynchronously
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(open_pje_tab, trt_number, paste)
                executor.submit(open_astrea_tab, paste)

        time.sleep(1)

except Exception as e:
    print(f"An error occurred: {e}")
