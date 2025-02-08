import os
import time
import base64
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

url = "https://pje.trt1.jus.br/consultaprocessual/captcha/detalhe-processo/0100356-73.2020.5.01.0058/1"
pasta_imagens = "C:/Users/fish/script_pje/treinamento"

if not os.path.exists(pasta_imagens):
    os.makedirs(pasta_imagens)

logging.basicConfig(
    level=logging.DEBUG,
    filename='captcha_downloader.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def download_captcha(driver):
    logging.debug(f"Requisitando URL: {url}")
    driver.get(url)

    try:
        # Wait for the captcha image to be present
        captcha_img = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "imagemCaptcha"))
        )
        img_src = captcha_img.get_attribute('src')
        logging.debug(f"Captcha image src: {img_src}")

        if img_src.startswith('data:image/png;base64,'):
            img_data = img_src.split(',')[1]
            img_data = base64.b64decode(img_data)
            timestamp = int(time.time())
            img_path = os.path.join(pasta_imagens, f'captcha_{timestamp}.png')
            with open(img_path, 'wb') as f:
                f.write(img_data)
            print(f"Captcha downloaded and saved to {img_path}")
            logging.info(f"Captcha downloaded and saved to {img_path}")
        else:
            print("Captcha image source is not base64 encoded")
            logging.error("Captcha image source is not base64 encoded")
    except Exception as e:
        print("Captcha image not found")
        logging.error("Captcha image not found")
        logging.error(str(e))

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    while True:
        download_captcha(driver)
        time.sleep(1)
finally:
    driver.quit()