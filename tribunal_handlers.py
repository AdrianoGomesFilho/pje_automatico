"""
Tribunal-specific handlers for different PJE systems
"""
import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import os
import sys
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Icon path setup (same as main file)
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(__file__)

ICON_PATH = os.path.join(BASE_PATH, "icon.ico")
TKINTER_ICON_PATH = ICON_PATH


def fetch_process_id(driver, id_url):
    """
    Fetch process ID from the PJE API.
    """
    driver.execute_script(f"window.open('{id_url}', '_blank');")
    id_url_handle = driver.window_handles[-1]
    driver.switch_to.window(id_url_handle)
    try:
        # Wait for the page to load and fetch the process ID from the HTML
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        process_id_element = soup.find('pre')
        if not process_id_element:
            raise ValueError("Process ID not found")
        # Try to parse the JSON
        data = json.loads(process_id_element.text.strip())
        # If the data is a dict and contains 'codigoErro', treat as error
        if isinstance(data, dict) and "codigoErro" in data:
            raise ValueError(f"Erro do PJE: {data.get('mensagem', 'Erro desconhecido')}")
        # If the data is a list, get the id as before
        process_id = data[0]['id']
        return process_id
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])


def prompt_for_pje_level_trabalhista(paste):
    """
    Prompt user to choose PJE level for trabalhista (TRT) processes.
    """
    pje_level_window = tk.Tk()
    pje_level_window.title("Escolha o Grau - Trabalhista")
    pje_level_window.attributes('-topmost', True)
    pje_level_window.configure(bg="#D9CDFF")

    # Set custom icon for the tkinter window
    pje_level_window.iconbitmap(TKINTER_ICON_PATH)

    screen_width = pje_level_window.winfo_screenwidth()
    screen_height = pje_level_window.winfo_screenheight()
    window_width = 300
    window_height = 300
    position_right = screen_width - window_width - 20
    position_down = screen_height - window_height - 80
    pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 12)

    tk.Label(pje_level_window, text=f"Detectado o processo\n{paste}", bg="#D9CDFF", fg="#484554", font=(font_style[0], font_style[1], "bold")).pack(pady=10)

    pje_level = tk.StringVar(value="Ignore")

    def select_level(level):
        pje_level.set(level)
        pje_level_window.destroy()

    tk.Button(pje_level_window, text="Primeiro Grau PJE", command=lambda: select_level("Primeiro grau PJE"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Segundo Grau PJE", command=lambda: select_level("Segundo grau PJE"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="TST PJE", command=lambda: select_level("TST PJE"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="TST Antigo", command=lambda: select_level("TST Antigo"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Ignorar e aguardar", command=lambda: select_level("Ignore"), bg="#CFCBE7", fg="#3F3D56", width=20, font=font_style).pack(pady=5)

    def on_close():
        pje_level.set("Ignore")
        pje_level_window.destroy()

    pje_level_window.protocol("WM_DELETE_WINDOW", on_close)

    pje_level_window.mainloop()
    return pje_level.get()


def prompt_for_pje_level_tjpe(paste):
    """
    Prompt user to choose PJE level for TJPE processes.
    """
    pje_level_window = tk.Tk()
    pje_level_window.title("Escolha o Grau - TJPE")
    pje_level_window.attributes('-topmost', True)
    pje_level_window.configure(bg="#D9CDFF")

    # Set custom icon for the tkinter window
    pje_level_window.iconbitmap(TKINTER_ICON_PATH)

    screen_width = pje_level_window.winfo_screenwidth()
    screen_height = pje_level_window.winfo_screenheight()
    window_width = 300
    window_height = 250
    position_right = screen_width - window_width - 20
    position_down = screen_height - window_height - 80
    pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 12)

    tk.Label(pje_level_window, text=f"Detectado processo TJPE\n{paste}", bg="#D9CDFF", fg="#484554", font=(font_style[0], font_style[1], "bold")).pack(pady=10)

    pje_level = tk.StringVar(value="Ignore")

    def select_level(level):
        pje_level.set(level)
        pje_level_window.destroy()

    tk.Button(pje_level_window, text="Primeiro grau TJPE", command=lambda: select_level("Primeiro grau TJPE"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Segundo grau TJPE", command=lambda: select_level("Segundo grau TJPE"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Ignorar e aguardar", command=lambda: select_level("Ignore"), bg="#CFCBE7", fg="#3F3D56", width=20, font=font_style).pack(pady=5)

    def on_close():
        pje_level.set("Ignore")
        pje_level_window.destroy()

    pje_level_window.protocol("WM_DELETE_WINDOW", on_close)

    pje_level_window.mainloop()
    return pje_level.get()


def prompt_for_pje_level_jfpe(paste):
    """
    Prompt user to choose PJE level for JFPE processes.
    """
    pje_level_window = tk.Tk()
    pje_level_window.title("Escolha o Grau - JFPE")
    pje_level_window.attributes('-topmost', True)
    pje_level_window.configure(bg="#D9CDFF")

    # Set custom icon for the tkinter window
    pje_level_window.iconbitmap(TKINTER_ICON_PATH)

    screen_width = pje_level_window.winfo_screenwidth()
    screen_height = pje_level_window.winfo_screenheight()
    window_width = 300
    window_height = 250
    position_right = screen_width - window_width - 20
    position_down = screen_height - window_height - 80
    pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 12)

    tk.Label(pje_level_window, text=f"Detectado processo JFPE\n{paste}", bg="#D9CDFF", fg="#484554", font=(font_style[0], font_style[1], "bold")).pack(pady=10)

    pje_level = tk.StringVar(value="Ignore")

    def select_level(level):
        pje_level.set(level)
        pje_level_window.destroy()

    tk.Button(pje_level_window, text="Primeira instância JFPE", command=lambda: select_level("Primeira instância JFPE"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="TRF5 JFPE", command=lambda: select_level("TRF5 JFPE"), bg="#A084E8", fg="#FFFFFF", width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Ignorar e aguardar", command=lambda: select_level("Ignore"), bg="#CFCBE7", fg="#3F3D56", width=20, font=font_style).pack(pady=5)

    def on_close():
        pje_level.set("Ignore")
        pje_level_window.destroy()

    pje_level_window.protocol("WM_DELETE_WINDOW", on_close)

    pje_level_window.mainloop()
    return pje_level.get()


def handle_trabalhista_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
    """
    Handle complete trabalhista login process including TST Antigo and process ID fetching.
    Returns: (success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
    """
    trt_number = paste[18:20]
    trt_number = trt_number.lstrip('0')
    
    # Handle TST Antigo case
    if pje_level == "TST Antigo":
        paste_parts = paste.split('-')
        numeroTst = paste_parts[0]
        remaining_parts = paste_parts[1].split('.')
        digitoTst = remaining_parts[0]
        anoTst = remaining_parts[1]
        orgaoTst = remaining_parts[2]
        tribunalTst = remaining_parts[3]
        varaTst = remaining_parts[4]
        base_url = f"https://consultaprocessual.tst.jus.br/consultaProcessual/consultaTstNumUnica.do?conscsjt=&numeroTst={numeroTst}&digitoTst={digitoTst}&anoTst={anoTst}&orgaoTst={orgaoTst}&tribunalTst={tribunalTst}&varaTst={varaTst}&consulta=Consultar"
        
        driver.switch_to.window(driver.window_handles[-1])
        driver.execute_script(f"window.open('{base_url}', '_blank');")
        time.sleep(3)
        notifier.send("TST Antigo - Caso esteja em consulta de terceiros, tente reabrir com a opcão 'TST PJE'")
        return True, None, None, True, False, False  # success, no process_id needed, break from loop
    
    # Regular PJE handling
    if pje_level == "Primeiro grau PJE":
        base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
        id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
    elif pje_level == "Segundo grau PJE":
        base_url = f"https://pje.trt{trt_number}.jus.br/segundograu/login.seam"
        id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
    elif pje_level == "TST PJE":
        base_url = "https://pje.tst.jus.br/tst/login.seam"
        id_url = f"https://pje.tst.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
    
    # Perform login and fetch process ID
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    
    try:
        botao_pdpj = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnSsoPdpj")))
        botao_pdpj.click()
        
        # Custom function to wait for either of two elements to be present
        def wait_for_any_element(driver, locators, timeout=10):
            for _ in range(timeout * 10):  # Check every 0.1 seconds
                for locator in locators:
                    try:
                        element = driver.find_element(*locator)
                        if element.is_displayed():
                            return element
                    except:
                        continue
                time.sleep(0.1)
            raise TimeoutException("Neither element was found within the timeout period.")

        # Wait for login elements
        elemento_login = wait_for_any_element(driver, [
            (By.ID, "kc-login"),
            (By.ID, "brasao-republica"),
            (By.ID, "formPesquisa")
        ])

        if elemento_login.get_attribute("id") == "kc-login":
            if login_method in ["4", "2"]:
                driver.find_element(By.CLASS_NAME, "botao-certificado-titulo").click()
                WebDriverWait(driver, 30).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.ID, "brasao-republica")),
                        EC.presence_of_element_located((By.ID, "formPesquisa"))
                    )
                )
                process_id = fetch_process_id(driver, id_url)
            else:
                driver.find_element(By.ID, "username").send_keys(usuario_pje)
                driver.find_element(By.ID, "password").send_keys(senha_pje)
                driver.find_element(By.ID, "kc-login").click()
                WebDriverWait(driver, 30).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.ID, "brasao-republica")),
                        EC.presence_of_element_located((By.ID, "formPesquisa"))
                    )
                )
                process_id = fetch_process_id(driver, id_url)
        elif elemento_login.get_attribute("id") in ["brasao-republica", "formPesquisa"]:
            process_id = fetch_process_id(driver, id_url)
        
        # Build final URL
        if pje_level == "TST PJE":
            final_url = f"https://pje.tst.jus.br/pjekz/processo/{process_id}/detalhe"
        else:
            final_url = f"https://pje.trt{trt_number}.jus.br/pjekz/processo/{process_id}/detalhe"
        
        return True, process_id, final_url, False, False, False  # success, continue normally
        
    except (ValueError, TimeoutException):
        return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado


def handle_tjpe_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
    """
    Handle complete TJPE login process including process ID fetching.
    Returns: (success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
    """
    if pje_level == "Primeiro grau TJPE":
        base_url = "https://pje.tjpe.jus.br/1g/login.seam"
        id_url = f"https://pje.tjpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
    elif pje_level == "Segundo grau TJPE":
        base_url = "https://pje.tjpe.jus.br/2g/login.seam"
        id_url = f"https://pje.tjpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
    
    # Perform login and fetch process ID
    success = perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method)
    
    if not success:
        return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
    
    try:
        process_id = fetch_process_id(driver, id_url)
        final_url = f"https://pje.tjpe.jus.br/pjekz/processo/{process_id}/detalhe"
        return True, process_id, final_url, False, False, False  # success
    except (ValueError, TimeoutException):
        return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado


def handle_jfpe_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
    """
    Handle complete JFPE login process including process ID fetching.
    Returns: (success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
    """
    if pje_level == "Primeira instância JFPE":
        base_url = "https://pje.jfpe.jus.br/pje/login.seam"
        id_url = f"https://pje.jfpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
    elif pje_level == "TRF5 JFPE":
        base_url = "https://pje.trf5.jus.br/pje/login.seam"
        id_url = f"https://pje.trf5.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
    
    # Perform login and fetch process ID
    success = perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method)
    
    if not success:
        return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
    
    try:
        process_id = fetch_process_id(driver, id_url)
        if pje_level == "Primeira instância JFPE":
            final_url = f"https://pje.jfpe.jus.br/pjekz/processo/{process_id}/detalhe"
        else:  # TRF5 JFPE
            final_url = f"https://pje.trf5.jus.br/pjekz/processo/{process_id}/detalhe"
        return True, process_id, final_url, False, False, False  # success
    except (ValueError, TimeoutException):
        return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado


def perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method):
    """
    Perform the actual PJE login process.
    This can be customized per tribunal type if needed.
    """
    driver.execute_script(f"window.open('{base_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    
    try:
        botao_pdpj = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnSsoPdpj")))
        botao_pdpj.click()
        
        # Custom function to wait for either of two elements to be present
        def wait_for_any_element(driver, locators, timeout=10):
            for _ in range(timeout * 10):  # Check every 0.1 seconds
                for locator in locators:
                    try:
                        element = driver.find_element(*locator)
                        if element.is_displayed():
                            return element
                    except:
                        continue
                time.sleep(0.1)
            raise TimeoutException("Neither element was found within the timeout period.")

        # Wait for login elements
        elemento_login = wait_for_any_element(driver, [
            (By.ID, "kc-login"),
            (By.ID, "brasao-republica"),
            (By.ID, "formPesquisa")
        ])

        if elemento_login.get_attribute("id") == "kc-login":
            if login_method in ["4", "2"]:
                driver.find_element(By.CLASS_NAME, "botao-certificado-titulo").click()
            else:
                driver.find_element(By.ID, "username").send_keys(usuario_pje)
                driver.find_element(By.ID, "password").send_keys(senha_pje)
                driver.find_element(By.ID, "kc-login").click()
            
            # Wait for successful login
            WebDriverWait(driver, 30).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "brasao-republica")),
                    EC.presence_of_element_located((By.ID, "formPesquisa"))
                )
            )
        
        return True
        
    except (TimeoutException, Exception) as e:
        print(f"Login failed: {e}")
        return False


def build_final_url(tribunal_type, pje_level, process_id, paste):
    """
    Build the final URL based on tribunal type and PJE level.
    """
    if tribunal_type == 'trabalhista':
        trt_number = paste[18:20].lstrip('0')
        if pje_level == "TST PJE":
            return f"https://pje.tst.jus.br/pjekz/processo/{process_id}/detalhe"
        else:
            return f"https://pje.trt{trt_number}.jus.br/pjekz/processo/{process_id}/detalhe"
    
    elif tribunal_type == 'tjpe':
        if pje_level == "Primeiro grau TJPE":
            return f"https://pje.tjpe.jus.br/pjekz/processo/{process_id}/detalhe"
        elif pje_level == "Segundo grau TJPE":
            return f"https://pje.tjpe.jus.br/pjekz/processo/{process_id}/detalhe"
    
    elif tribunal_type == 'jfpe':
        if pje_level == "Primeira instância JFPE":
            return f"https://pje.jfpe.jus.br/pjekz/processo/{process_id}/detalhe"
        elif pje_level == "TRF5 JFPE":
            return f"https://pje.trf5.jus.br/pjekz/processo/{process_id}/detalhe"
    
    return None
