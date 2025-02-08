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
import pytesseract
from PIL import Image
import base64
from io import BytesIO

# Load credentials from .env file
load_dotenv('credenciais.env')
print("Loaded .env file")

#test

# Get credentials from environment variables
usuario = os.getenv("USERNAMEASTREA")
senha = os.getenv("PASSWORDASTREA")
print(f"Username: {usuario}")
print(f"Password: xxxxxxxxxxxx")

# Load PJE credentials from another .env file
load_dotenv('credenciais_pje.env')
usuario_pje = os.getenv("USERNAMEPJE")
senha_pje = os.getenv("PASSWORDPJE")
print(f"PJE Username: {usuario_pje}")
print(f"PJE Password: xxxxxxxxxxxx")

# Specify the path to your Chrome user data directory
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
chrome_options.add_argument("--start-maximized")  # Open browser in fullscreen

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Store the last clipboard content
last_clipboard_content = ""

def find_or_open_tab(driver, base_url, data_url=None):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if (base_url in driver.current_url or (data_url and data_url in driver.current_url)):
            return handle
    # Switch to the last tab before opening a new one
    driver.switch_to.window(driver.window_handles[-1])
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    new_handle = driver.window_handles[-1]
    return new_handle

def solve_captcha(image_base64):
    try:
        print("Solving captcha...")
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        captcha_text = pytesseract.image_to_string(image, config='--psm 6')
        captcha_text = re.sub(r'[^a-z0-9]', '', captcha_text.lower())  # Remove non-alphanumeric characters and convert to lowercase
        print(f"Captcha text: {captcha_text}")
        return captcha_text.strip()
    except Exception as e:
        print(f"Error solving captcha: {e}")
        return ""

try:
    while True:
        try:
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

                # Extract the TRT number (15th and 16th characters)
                trt_number = paste[18:20]
                print(f"TRT number extracted: {trt_number}")

                # Remove leading zero if present
                trt_number = trt_number.lstrip('0')
                print(f"TRT number after stripping leading zero: {trt_number}")

                # Construct the base URL dynamically
                base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
                print(f"Base URL constructed: {base_url}")

                # Find or open the tab for base_url
                base_url_handle = find_or_open_tab(driver, base_url)
                driver.switch_to.window(base_url_handle)
                print(f"Switched to base URL tab: {base_url_handle}")

                # Wait for the "modo-operacao" element to be present
                modo_operacao_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "modo-operacao")))
                print("Modo operacao element found")

                # Fill the input id=username with credentials (USERNAMEPJE)
                driver.find_element(By.ID, "username").send_keys(usuario_pje)
                print("Username filled")
                # Fill the input id=password with credentials (PASSWORDPJE)
                driver.find_element(By.ID, "password").send_keys(senha_pje)
                print("Password filled")
                # Press the button id=btnEntrar
                driver.find_element(By.ID, "btnEntrar").click()
                print("Login button clicked")

                final_url = f"https://pje.trt{trt_number}.jus.br/consultaprocessual/detalhe-processo/{paste}"
                print(f"Final URL constructed: {final_url}")

                # Open the final URL in a new tab and close the base URL tab
                driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                driver.execute_script(f"window.open('{final_url}', '_blank');")
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
                print("Switched to final URL tab")

                # Wait for the "painel-escolha-processo" element to be present
                painel_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "painel-escolha-processo"))
                )
                print("Painel escolha processo element found")

                # Click the desired button (e.g., the first button)
                buttons = driver.find_elements(By.CLASS_NAME, "selecao-processo")
                if buttons:
                    print("Process selection buttons found")
                    print("Waiting for user to select a process...")

                    # Wait for the user to select a process
                    WebDriverWait(driver, 300).until(
                        EC.staleness_of(buttons[0])
                    )
                    print("User has selected a process")

                    # Wait for the URL to contain "captcha"
                    WebDriverWait(driver, 300).until(
                        EC.url_contains("captcha")
                    )
                    print("Captcha detected in URL")

                    # Wait for the captcha to appear
                    captcha_image_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "imagemCaptcha"))
                    )
                    captcha_image_src = captcha_image_element.get_attribute("src")
                    print(f"Captcha image src: {captcha_image_src}")

                    try:
                        captcha_image = captcha_image_src.split(",")[1]
                        print("Captcha image found")
                    except IndexError:
                        print("Error: Captcha image src is not in the expected format")
                        continue

                    # Retry mechanism for solving captcha
                    for attempt in range(3):  # Retry up to 3 times
                        print(f"Attempt {attempt + 1} to solve captcha")
                        captcha_solution = solve_captcha(captcha_image)
                        if captcha_solution:
                            driver.find_element(By.ID, "captchaInput").send_keys(captcha_solution)
                            submit_button = driver.find_element(By.ID, "btnEnviar")
                            submit_button.click()
                            print("Submit button clicked")
                            time.sleep(2)  # Wait for the page to process the captcha
                            if not driver.find_elements(By.ID, "btnEnviar"):
                                print("Captcha solved and submitted")
                                break
                            else:
                                print(f"Captcha not solved on attempt {attempt + 1}")
                                # Wait for the new captcha to appear
                                captcha_image_element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "imagemCaptcha"))
                                )
                                captcha_image_src = captcha_image_element.get_attribute("src")
                                print(f"New captcha image src: {captcha_image_src}")
                                try:
                                    captcha_image = captcha_image_src.split(",")[1]
                                    print("New captcha image found")
                                except IndexError:
                                    print("Error: New captcha image src is not in the expected format")
                                    continue
                        else:
                            print(f"Failed to solve captcha on attempt {attempt + 1}")
                        time.sleep(2)  # Wait before retrying
                    else:
                        print("Failed to solve captcha after 3 attempts")
                else:
                    print("No process selection buttons found")

                # Split the paste value into the respective fields
                paste_parts = paste.split('-')
                numeroTst = paste_parts[0]
                remaining_parts = paste_parts[1].split('.')
                digitoTst = remaining_parts[0]
                anoTst = remaining_parts[1]
                orgaoTst = remaining_parts[2]
                tribunalTst = remaining_parts[3]
                varaTst = remaining_parts[4]

                # Construct the iframe URL
                iframe_url = f"https://consultaprocessual.tst.jus.br/consultaProcessual/consultaTstNumUnica.do?conscsjt=&numeroTst={numeroTst}&digitoTst={digitoTst}&anoTst={anoTst}&orgaoTst={orgaoTst}&tribunalTst={tribunalTst}&varaTst={varaTst}&consulta=Consultar"
                
                
                # Add the title and iframe to the end of the body element
                driver.execute_script("""
                    var titleDiv = document.createElement('div');
                    titleDiv.innerHTML = '<h2>Consulta no TST (sistema antigo)</h2>';
                    titleDiv.style.marginTop = '550px';
                    document.body.appendChild(titleDiv);

                    var iframe = document.createElement('iframe');
                    iframe.src = arguments[0];
                    iframe.width = '100%';
                    iframe.height = '800px';
                    iframe.style.border = '2px solid black';
                    iframe.style.marginTop = '20px';
                    document.body.appendChild(iframe);

                """, iframe_url)

        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
        finally:
            time.sleep(1)  # Wait before checking the clipboard again

except Exception as e:
    print(f"An error occurred: {e}")