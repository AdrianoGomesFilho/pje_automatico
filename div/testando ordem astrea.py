import time
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv('credenciais.env')
print("Loaded .env file")

# Get credentials from environment variables
usuario = os.getenv("USERNAMEASTREA")
senha = os.getenv("PASSWORDASTREA")
print(f"Username: {usuario}")
print(f"Password: xxxxxxxxxxxx")

def start_browser():
    """
    Initialize a new instance of the Chrome browser with specific options.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
    chrome_options.add_argument("start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def open_new_tab(driver, url):
    """
    Open a new tab in the browser with the specified URL.
    """
    driver.execute_script(f"window.open('{url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

def login_astrea(driver):
    """
    Log into the Astrea platform using the provided credentials.
    """
    try:
        login_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Fill in the credentials and submit the form
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(usuario)
        password_field.send_keys(senha)

        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        print("Logged in to Astrea successfully.")
    except Exception as e:
        print("Login page not detected or error during login:", e)

def monitor_clipboard(driver):
    """
    Continuously monitor the clipboard for specific data patterns and perform actions accordingly.
    """
    last_clipboard_content = ""
    pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')

    while True:
        try:
            paste = pyperclip.paste()

            if paste != last_clipboard_content and pattern.match(paste):
                print(f"Processo identificado: {paste}")

                last_clipboard_content = paste
                trt_number = paste[18:20].lstrip('0')
                astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"

                open_new_tab(driver, astrea_url)
                login_astrea(driver)
                base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
                open_new_tab(driver, base_url)

                modo_operacao_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modo-operacao")))
                modo_operacao_element.click()
                buttons = driver.find_elements(By.XPATH, "//*[contains(@id, 'UtilizarPjeOffice')]")
                button_id = buttons[0].get_attribute('id')
                button_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, button_id)))
                driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, button_id))).click()

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "nome-usuario")))

                final_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"
                open_new_tab(driver, final_url)

                # Close the base_url tab and return to the Astrea tab
                driver.close()
            time.sleep(1)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Continue running the script without quitting the browser
            driver.get("about:blank")

if __name__ == "__main__":
    driver = start_browser()
    monitor_clipboard(driver)
