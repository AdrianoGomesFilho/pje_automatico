"""
JFPE (Justiça Federal de Pernambuco) tribunal handler
"""
import tkinter as tk
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_handler import BaseTribunalHandler


class JfpeHandler(BaseTribunalHandler):
    """
    Handler for JFPE (Justiça Federal de Pernambuco) processes.
    """
    
    def __init__(self):
        super().__init__("JFPE")
    
    def prompt_for_pje_level(self, paste):
        """
        Prompt user to choose PJE level for JFPE processes.
        """
        pje_level_window, font_style = self.create_prompt_window("Escolha o Grau - JFPE", paste, 300)
        
        pje_level = tk.StringVar(value="Ignore")

        def select_level(level):
            pje_level.set(level)
            pje_level_window.destroy()

        # Add tribunal-specific buttons
        self.add_button(pje_level_window, "Juizado Primeiro grau", lambda: select_level("Juizado Primeiro grau"), font_style)
        self.add_button(pje_level_window, "Juizado Turma Recursal", lambda: select_level("Juizado Turma Recursal"), font_style)
        
        # Add ignore button
        self.add_ignore_button(pje_level_window, pje_level, font_style)

        pje_level_window.mainloop()
        return pje_level.get()
    
    def handle_login(self, driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
        if pje_level == "Juizado Primeiro grau":
            base_url = "https://pje1g.trf5.jus.br/pje/login.seam"
            search_url = "https://pje1g.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
        
        elif pje_level == "Juizado Turma Recursal":
            base_url = "https://pje2g.trf5.jus.br/pje/login.seam"
            search_url = "https://pje2g.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
        
        else:
            return False, None, None, True, False, False
        
        try:
            # Open the PJE URL in a new tab
            driver.execute_script(f"window.open('{base_url}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)  # Give more time for page to load

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ssoFrame"))
            )
                    
            sso_iframe = driver.find_element(By.ID, "ssoFrame")
            driver.switch_to.frame(sso_iframe)
            
            time.sleep(3)
            
            # Check what's in the iframe
            iframe_source = driver.page_source
            
            certificate_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "kc-pje-office"))
            )

            certificate_button.click()
    
            WebDriverWait(driver, 15).until( 
                EC.presence_of_element_located((By.CLASS_NAME, "avatar"))
            )
            
            driver.get(search_url)
            
            # Parse the process number (format: NNNNNNN-DD.AAAA.J.TR.OOOO)
            # Example: 0800001-23.2023.4.05.8105
            try:
                # Remove any spaces and split the process number
                clean_paste = paste.replace(" ", "").strip()
                parts = clean_paste.split('-')
                main_number = parts[0]  # NNNNNNN
                rest_parts = parts[1].split('.')
                
                numero_sequencial = main_number  # 0800001
                digito_verificador = rest_parts[0]  # 23
                ano = rest_parts[1]  # 2023
                ramo_justica = rest_parts[2]  # 4 (already filled)
                tribunal = rest_parts[3]  # 05 (already filled)
                orgao_justica = rest_parts[4]  # 8105
                
                # Wait for the form to load and fill the fields
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "fPP:numeroProcesso:numeroSequencial"))
                )
                
                # Fill each field
                driver.find_element(By.ID, "fPP:numeroProcesso:numeroSequencial").clear()
                driver.find_element(By.ID, "fPP:numeroProcesso:numeroSequencial").send_keys(numero_sequencial)
                
                driver.find_element(By.ID, "fPP:numeroProcesso:numeroDigitoVerificador").clear()
                driver.find_element(By.ID, "fPP:numeroProcesso:numeroDigitoVerificador").send_keys(digito_verificador)
                
                driver.find_element(By.ID, "fPP:numeroProcesso:Ano").clear()
                driver.find_element(By.ID, "fPP:numeroProcesso:Ano").send_keys(ano)
                
                driver.find_element(By.ID, "fPP:numeroProcesso:NumeroOrgaoJustica").clear()
                driver.find_element(By.ID, "fPP:numeroProcesso:NumeroOrgaoJustica").send_keys(orgao_justica)
                
                # Click the search button
                search_button = driver.find_element(By.ID, "fPP:searchProcessos")
                search_button.click()
                
                # Wait for search results
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-link.btn-condensed"))
                )
                # Get the first result link
                first_result = driver.find_element(By.CSS_SELECTOR, ".btn-link.btn-condensed")
                first_result.click()
                    
            except Exception as parse_error:
                print(f"[DEBUG] Error parsing process number: {parse_error}")
                return False, None, None, False, True, True
            
        except TimeoutException:
            notifier.show_toast("JFPE Login", "Timeout durante o login JFPE")
            return False, None, None, True, False, False
        except Exception as e:
            print(f"[DEBUG] JFPE login error: {e}")
            notifier.show_toast("JFPE Login", f"Erro no login JFPE: {str(e)}")
            return False, None, None, True, False, False
        
