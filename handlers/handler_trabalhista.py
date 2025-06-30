"""
Trabalhista (TRT/TST) tribunal handler
"""
import tkinter as tk
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base_handler import BaseTribunalHandler


class TrabalhistaHandler(BaseTribunalHandler):
    """
    Handler for Trabalhista (TRT/TST) processes.
    """
    
    def __init__(self):
        super().__init__("Trabalhista")
    
    def prompt_for_pje_level(self, paste):
        """
        Prompt user to choose PJE level for trabalhista (TRT) processes.
        """
        pje_level_window, font_style = self.create_prompt_window("Escolha o Grau - Trabalhista", paste, 300)
        
        pje_level = tk.StringVar(value="Ignore")

        def select_level(level):
            pje_level.set(level)
            pje_level_window.destroy()

        # Add tribunal-specific buttons
        self.add_button(pje_level_window, "Primeiro Grau PJE", lambda: select_level("Primeiro grau PJE"), font_style)
        self.add_button(pje_level_window, "Segundo Grau PJE", lambda: select_level("Segundo grau PJE"), font_style)
        self.add_button(pje_level_window, "TST PJE", lambda: select_level("TST PJE"), font_style)
        self.add_button(pje_level_window, "TST Antigo", lambda: select_level("TST Antigo"), font_style)
        
        # Add ignore button
        self.add_ignore_button(pje_level_window, pje_level, font_style)

        pje_level_window.mainloop()
        return pje_level.get()
    
    def handle_login(self, driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
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
            driver.switch_to.window(driver.window_handles[-1])
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
                    process_id = self.fetch_process_id(driver, id_url)
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
                    process_id = self.fetch_process_id(driver, id_url)
            elif elemento_login.get_attribute("id") in ["brasao-republica", "formPesquisa"]:
                process_id = self.fetch_process_id(driver, id_url)
            
            # Build final URL
            if pje_level == "TST PJE":
                final_url = f"https://pje.tst.jus.br/pjekz/processo/{process_id}/detalhe"
            else:
                final_url = f"https://pje.trt{trt_number}.jus.br/pjekz/processo/{process_id}/detalhe"
            
            return True, process_id, final_url, False, False, False  # success, continue normally
            
        except (ValueError, TimeoutException):
            return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
