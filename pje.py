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
            
            # Construct the URL dynamically
            url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
            
            # Open a new tab and navigate to the target URL
            driver.execute_script(f"window.open('{url}', '_blank');")

            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])

            # Wait for the "btn-link" button to be clickable and click it
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "modo-operacao"))).click()
            
            try:
                # Wait for the "j_id112:btnUtilizarPjeOffice" button to be clickable and click it
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_id111:btnUtilizarPjeOffice"))).click()
            except TimeoutException:
                # If the first ID is not present, select the alternative ID
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "j_id112:btnUtilizarPjeOffice"))).click()

            # Wait for the "loginAplicacaoButton" button to be clickable and click it
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))).click()
            
            # Wait for 5 seconds to handle the popup
            time.sleep(5)
            
            # Wait for the element by name "Consulta Processos de Terceiros" to be present and click it
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Consulta Processos de Terceiros"))).click()
            
            # Wait for the "nrProcessoField" input field to be present and focus on it
            nr_processo_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nrProcessoField")))
            driver.execute_script("arguments[0].focus();", nr_processo_field)
            
            # Paste the clipboard content into the focused input field
            driver.execute_script("arguments[0].value = arguments[1];", nr_processo_field, paste)
            
            # Click the "btnPesquisar" button
            driver.find_element(By.ID, "btnPesquisar").click()
            
            time.sleep(5)  # Wait for a few seconds before checking the clipboard again

        time.sleep(1)  # Wait before checking the clipboard again

except Exception as e:
    print(f"An error occurred: {e}")
