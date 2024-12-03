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

def find_or_open_tab(driver, base_url):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if base_url in driver.current_url:
            return handle
    # If the tab is not found, open a new one
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    new_handle = driver.window_handles[-1]
    return new_handle

def add_tst_button_if_not_present(driver, paste):
    try:
        # Check if the button with text "TST" is present
        buttons = driver.find_elements(By.TAG_NAME, "button")
        if not any("TST" in button.text for button in buttons):
            # Create a new button element
            driver.execute_script("""
                var button = document.createElement('button');
                button.innerHTML = 'TST - Ser direcionado ao site do TST antigo';
                button.id = 'tst_button';
                button.style = 'margin: 10px; padding: 10px; background-color: #4CAF50; color: white; border: none; cursor: pointer;';
                document.body.appendChild(button);
            """)
            print("TST button added.")
            
            # Add event listener to the button
            driver.execute_script(f"""
                document.getElementById('tst_button').addEventListener('click', function() {{
                    var newWindow = window.open('https://visualizacao-autos.tst.jus.br/visualizacaoAutos/ConsultarProcesso.do?load=1', '_blank');
                    newWindow.onload = function() {{
                        var paste = '{paste}';
                        var parts = paste.split(/[-.]/);
                        newWindow.document.getElementsByName('numProc')[0].value = parts[0];
                        newWindow.document.getElementsByName('digito')[0].value = parts[1];
                        newWindow.document.getElementsByName('anoProc')[0].value = parts[2];
                        newWindow.document.getElementsByName('justica')[0].value = parts[3];
                        newWindow.document.getElementsByName('numTribunal')[0].value = parts[4];
                        newWindow.document.getElementsByName('numVara')[0].value = parts[5];
                        newWindow.document.querySelector('input[type="submit"]').click();
                    }};
                }}); 
            """)
            print("Event listener added to TST button.")
    except Exception as e:
        print(f"Error adding TST button: {e}")

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

            # Construct the base URL dynamically
            base_url = f"https://pje.tst.jus.br/consultaprocessual/detalhe-processo/{paste}"
            
            # Find or open the tab for base_url
            base_url_handle = find_or_open_tab(driver, base_url)
            driver.switch_to.window(base_url_handle)
            
            # Add TST button if not present
            add_tst_button_if_not_present(driver, paste)
            
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
