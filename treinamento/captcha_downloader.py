import requests
import time
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import logging

url = "https://pje.trt5.jus.br/consultaprocessual/captcha/detalhe-processo/0000332-73.2021.5.05.0031/1"
save_folder = "c:/Users/fish/script_pje/treinamento"

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

base_url = "https://pje.trt5.jus.br"

logging.basicConfig(level=logging.DEBUG, filename='captcha_downloader.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

def download_captcha():
    logging.debug(f"Requesting URL: {url}")
    response = requests.get(url, headers=headers)
    logging.debug(f"Response status code: {response.status_code}")
    logging.debug(f"Response content: {response.content}")
    time.sleep(2)  # Add delay to allow the site to load properly
    soup = BeautifulSoup(response.content, 'html.parser')
    captcha_img = soup.find('img', {'id': 'imagemCaptcha'})
    print(captcha_img)
    logging.debug(f"Captcha image tag: {captcha_img}")
    if captcha_img:
        img_url = captcha_img['src']
        if img_url.startswith('/'):
            img_url = urljoin(url, img_url)
        logging.debug(f"Captcha image URL: {img_url}")
        print(img_url)
        img_response = requests.get(img_url, headers=headers)
        logging.debug(f"Image response status code: {img_response.status_code}")
        logging.debug(f"Image response content: {img_response.content}")
        if img_response.status_code == 200:
            img_path = os.path.join(save_folder, 'captcha.png')
            with open(img_path, 'wb') as f:
                f.write(img_response.content)
            print(f"Captcha downloaded and saved to {img_path}")
            logging.info(f"Captcha downloaded and saved to {img_path}")
        else:
            print("Failed to download captcha image")
            logging.error("Failed to download captcha image")
    else:
        print("Captcha image not found")
        logging.error("Captcha image not found")
        print(soup.prettify())  # Print the HTML content for debugging
        with open("debug.html", "w", encoding="utf-8") as file:
            file.write(soup.prettify())  # Save the HTML content to a file for further inspection
        logging.debug("HTML content saved to debug.html")

while True:
    download_captcha()
    time.sleep(1)