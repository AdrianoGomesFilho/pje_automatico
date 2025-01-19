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
import pytesseract
from PIL import Image
import base64
from io import BytesIO

# Set the TESSDATA_PREFIX environment variable
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR'

# Specify the path to your Chrome user data directory
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
chrome_options.add_argument("--start-maximized")  # Open browser in fullscreen

# Initialize WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print(f"TESSDATA_PREFIX is set to: {os.environ.get('TESSDATA_PREFIX')}")
print(f"Tesseract cmd is set to: {pytesseract.pytesseract.tesseract_cmd}")

# Example with multiple languages
custom_config = r'--tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata" -l eng'

def solve_captcha(image_base64):
    try:
        print("Solving captcha...")
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        captcha_text = pytesseract.image_to_string(image, config=custom_config)
        captcha_text = re.sub(r'[^a-z0-9]', '', captcha_text.lower())  # Remove non-alphanumeric characters and convert to lowercase
        print(f"Captcha text: {captcha_text}")
        return captcha_text.strip()
    except Exception as e:
        print(f"Error solving captcha: {e}")
        return ""

# Debug section to open the specified URL and solve the captcha
debug_url = ""
driver.get(debug_url)
print(f"Opened debug URL: {debug_url}")

try:
    # Wait for the captcha to appear
    captcha_image_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "imagemCaptcha"))
    )
    captcha_image_src = captcha_image_element.get_attribute("src")

    try:
        captcha_image = captcha_image_src.split(",")[1]
        print("Captcha image found")
    except IndexError:
        print("Error: Captcha image src is not in the expected format")

    # Retry mechanism for solving captcha
    for attempt in range(10):  # Retry up to 10 times
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
        else:
            print(f"Failed to solve captcha on attempt {attempt + 1}")
        time.sleep(2)  # Wait before retrying
    else:
        print("Failed to solve captcha after 10 attempts")
except TimeoutException:
    print("Captcha image not found within the timeout period")

except KeyboardInterrupt:
    print("Program interrupted by user")
finally:
    driver.quit()