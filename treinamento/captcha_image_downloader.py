import os
import time
import base64
from selenium import webdriver #controla o browser
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By #usado para localizar elementos na página
from selenium.webdriver.support.ui import WebDriverWait #usado para esperar (tempo) por condições específicas antes de executar o próximo comando
from selenium.webdriver.support import expected_conditions as EC #usado para definir condições esperadas antes de executar o próximo comando
from webdriver_manager.chrome import ChromeDriverManager #usado para instalar o driver do Chrome automaticamente, caso não esteja instalado

url = "https://pje.trt1.jus.br/consultaprocessual/captcha/detalhe-processo/0100356-73.2020.5.01.0058/1"
pasta_imagem = "C:/Users/fish/script_pje/treinamento/imagens"

if not os.path.exists(pasta_imagem):
    os.makedirs(pasta_imagem) #cria a pasta caso ela não exista

def download_captcha(driver):
    driver.get(url) #acessa a página do captcha

    try:
        # Espera até que a imagem do captcha esteja presente
        captcha_img = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "imagemCaptcha"))
        )
        img_src = captcha_img.get_attribute('src') #pega o atributo src da imagem

        if img_src.startswith('data:image/png;base64,'):
            dados_imagem = img_src.split(',')[1] #pega a parte do base64 da imagem (1) (tudo que vier depois da virgula)
            dados_imagem = base64.b64decode(dados_imagem)#decodifica a imagem usando a library base64
            timestamp = int(time.time())#pega o timestamp atual, para que o nome do arquivo seja único, converte para integer para evitar pontos flutuantes
            caminho_imagem = os.path.join(pasta_imagem, f'captcha_{timestamp}.png') #cria o caminho do arquivo
            with open(caminho_imagem, 'wb') as arquivo: #abre o arquivo no modo de escrita binária (write binary - wb)
                arquivo.write(dados_imagem) #escreve a imagem no arquivo
            print(f"Imagem baixada e salva em {caminho_imagem}")
        else:
            print("A imagem não está codificada em base64")
    except Exception as e:
        print("A imagem não está codificada em base64")
        print(str(e))

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #instancia o driver do Chrome

try:
    while True: #o que deve ser true: o loop infinito, que só será interrompido manualmente
        download_captcha(driver)
        time.sleep(1)  #espera 1 segundo antes de executar o próximo comando
finally:
    driver.quit() #fecha o browser
