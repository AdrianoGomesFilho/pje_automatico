import time
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from dotenv import load_dotenv

# Specify the path to your external .env file
load_dotenv()
print("Loaded .env file")

# Get credentials from environment variables
usuario = os.getenv("USERNAMEASTREA")
senha = os.getenv("PASSWORDASTREA")
print(f"Username: {usuario}")
print(f"Password: {senha}")

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
            
            # Check the text of the "modo-operacao" element
            if "Modo de assinatura: Shodō" in modo_operacao_element.text:
                modo_operacao_element.click()
                
                try:
                    # Wait for the "j_id112:btnUtilizarPjeOffice" button to be clickable and click it
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_id111:btnUtilizarPjeOffice"))).click()
                except TimeoutException:
                    # If the first ID is not present, select the alternative ID
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_id112:btnUtilizarPjeOffice"))).click()

            # Wait for the "loginAplicacaoButton" button to be clickable and click it
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()

            ###### PJE TOKEN UNICO ##############################################

           
            meu_painel_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Meu Painel")))
            meu_painel_button.click()

            input_numero_processo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "inputNumeroProcesso")))

            input_numero_processo.clear()  # Clear any pre-existing text
            input_numero_processo.send_keys(paste)

            detalhes_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[mattooltip='Detalhes do Processo']")))
                
            if detalhes_button:
                detalhes_button.click()
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            else:
                # Construct the final URL with the specific data pattern appended
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
