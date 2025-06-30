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
        
        pje_level = tk.StringVar(value="")

        def select_level(level):
            pje_level.set(level)
            pje_level_window.destroy()

        # Add tribunal-specific buttons
        self.add_button(pje_level_window, "Juizado Primeiro grau", lambda: select_level("Juizado Primeiro grau"), font_style)
        self.add_button(pje_level_window, "Juizado Turma Recursal", lambda: select_level("Juizado Turma Recursal"), font_style)
        self.add_button(pje_level_window, "Justiça Federal Comum", lambda: select_level("Justiça Federal Comum"), font_style)
        
        # Add ignore button (no need for duplicate "Ignorar" button)
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
        
        elif pje_level == "Justiça Federal Comum":
            base_url = "https://pje.trf5.jus.br/pje/login.seam"
            search_url = "https://pje.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
        
        elif pje_level == "Ignore":
            return True, None, None, True, False, False  # Just wait for clipboard 

        
        try:
            # Open the PJE URL in a new tab
            try:
                driver.execute_script(f"window.open('{base_url}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
            except Exception as tab_error:
                # If tab management fails, navigate in current tab
                print(f"[DEBUG] Tab management failed, using current tab: {tab_error}")
                driver.get(base_url)

            # Different login flow for Justiça Federal Comum
            if pje_level == "Justiça Federal Comum":
                try:
                    login_element = WebDriverWait(driver, 10).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.ID, "nomeUsuario")),
                            EC.presence_of_element_located((By.ID, "loginAplicacaoButton"))
                        )
                    )
                except TimeoutException:
                    print("[DEBUG] Page took too long to load - showing reopen interface")
                    notifier.send("JFPE - Página demorou para carregar. Tente reabrir.")
                    return True, None, None, True, False, False  # Show reopen interface
                
                # Check which element was found
                try:
                    nome_usuario = driver.find_element(By.ID, "nomeUsuario")
                    print("[DEBUG] Already logged in - nomeUsuario found")
                except:
                    print("[DEBUG] Not logged in - proceeding with login")
                    # Need to login - click the loginAplicacaoButton
                    try:
                        # Handle popups dynamically
                        print("[DEBUG] Checking for popups...")
                        
                        # Check if first popup exists (may not appear on subsequent attempts)
                        try:
                            utilizar_btn = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable((By.ID, "btnUtilizarApplet"))
                            )
                            utilizar_btn.click()
                            print("[DEBUG] First popup found and clicked (btnUtilizarApplet)")
                        except:
                            print("[DEBUG] First popup not present, skipping (this is normal on subsequent attempts)")
                        
                        time.sleep(2)
                        
                        # Remove blocking container if present
                        try:
                            panel_container = driver.find_element(By.ID, "panelAmbienteContainer")
                            driver.execute_script("arguments[0].remove();", panel_container)
                            print("[DEBUG] Removed blocking overlay (panelAmbienteContainer)")
                        except:
                            print("[DEBUG] No blocking overlay to remove")
                        
                        # Click login button - try 3 times
                        for attempt in range(3):
                            try:
                                login_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.ID, "loginAplicacaoButton"))
                                )
                                login_button.click()
                                print("[DEBUG] Clicked loginAplicacaoButton")
                                break
                            except:
                                # Try JavaScript click as fallback
                                try:
                                    login_button = driver.find_element(By.ID, "loginAplicacaoButton")
                                    driver.execute_script("arguments[0].click();", login_button)
                                    print("[DEBUG] Used JavaScript click")
                                    break
                                except:
                                    if attempt == 2:
                                        raise Exception("Could not click login button")
                                    time.sleep(2)
                        
                        # Wait for password field (nomeUsuario) to appear after login
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.ID, "nomeUsuario"))
                        )
                        print("[DEBUG] Login form loaded - password field (nomeUsuario) found")
                        
                    except TimeoutException:
                        print("[DEBUG] Timeout waiting for login elements in Justiça Federal Comum")
                        notifier.send("JFPE - Timeout ao carregar login da Justiça Federal Comum")
                        return True, None, None, True, False, False
                
                # Navigate to search URL and fill the form for Justiça Federal Comum
                driver.get(search_url)
                
                try:
                    # Wait for the search form to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "consultarProcessoForm:numeroProcessoDecoration:numeroProcesso"))
                    )
                    
                    # Fill the process number field
                    process_field = driver.find_element(By.ID, "consultarProcessoForm:numeroProcessoDecoration:numeroProcesso")
                    
                    print(f"[DEBUG] Sending keys to process field: '{paste}'")
                    
                    # Clear and position cursor at the very beginning of the field
                    process_field.clear()
                    process_field.click()
                    time.sleep(0.2)
                    
                    # Move cursor to the very beginning of the field
                    driver.execute_script("arguments[0].setSelectionRange(0, 0);", process_field)
                    driver.execute_script("arguments[0].focus();", process_field)
                    
                    # Send the original paste data (with dashes and dots)
                    print(f"[DEBUG] Sending original paste data: '{paste}'")
                    process_field.send_keys(paste)
                    
                    # Verify the field was filled correctly
                    field_value = process_field.get_attribute("value")
                    print(f"[DEBUG] Field value after input: '{field_value}'")
                    
                    # Add a small delay before clicking search to ensure the value is registered
                    time.sleep(1)
                    
                    # Click the search button
                    search_button = driver.find_element(By.ID, "consultarProcessoForm:searchButton")
                    search_button.click()

                    # Wait for search results and extract the process details URL
                    try:
                        print("[DEBUG] Waiting for search results...")
                        # Wait for the first row to appear
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".rich-table-row.rich-table-firstrow"))
                        )
                        
                        # Find the "Ver Detalhes" image in the first row
                        ver_detalhes_img = driver.find_element(By.CSS_SELECTOR, "img[title='Ver Detalhes']")
                        
                        # Get the onclick attribute which contains the URL
                        onclick_attr = ver_detalhes_img.get_attribute("onclick")
                        
                        # Extract the URL from the onclick attribute
                        # onclick looks like: openPopUp('13101popUpDetalhesProcessoTrf', '/pje/Processo/ConsultaProcesso/Detalhe/listProcessoCompletoAdvogado.seam?idProcessoTrf=13101');
                        import re
                        url_match = re.search(r"'(/pje/Processo/ConsultaProcesso/Detalhe/listProcessoCompletoAdvogado\.seam\?idProcessoTrf=\d+)'", onclick_attr)
                        
                        if url_match:
                            relative_url = url_match.group(1)
                            # Form the complete URL
                            complete_url = f"https://pje.trf5.jus.br{relative_url}"
                            
                            # Open the process details page in a new tab
                            try:
                                driver.execute_script(f"window.open('{complete_url}', '_blank');")
                                print(f"[DEBUG] Opened process details in new tab: {complete_url}")
                                
                                # Close the current search results tab
                                if len(driver.window_handles) > 1:
                                    self.safe_close_tab(driver)
                                
                                # Switch to the new process details tab
                                self.safe_switch_to_last_window(driver)
                                print("[DEBUG] Switched to process details tab")
                            except Exception as tab_error:
                                print(f"[DEBUG] Tab management failed: {tab_error}")
                                # Fallback to navigate in current tab
                                driver.get(complete_url)
                        else:
                            print("[DEBUG] Could not extract process details URL from onclick attribute")
                            return False, None, None, False, True, True
                            
                    except Exception as extract_error:
                        print(f"[DEBUG] Error extracting process details URL: {extract_error}")
                        return False, None, None, False, True, True
                except Exception as search_error:
                    print(f"[DEBUG] Error searching process in Justiça Federal Comum: {search_error}")
                    return False, None, None, False, True, True
                
                # Return success for Justiça Federal Comum (no further processing needed)
                return True, None, None, False, False, False

            ######JUIZADO PRIMEIRO GRAU OR TURMA RECUSAL########   
            else:
                try:
                    login_element = WebDriverWait(driver, 10).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CLASS_NAME, "avatar")),
                            EC.presence_of_element_located((By.ID, "ssoFrame"))
                        )
                    )
                except TimeoutException:
                    print("[DEBUG] Page took too long to load - showing reopen interface")
                    notifier.send("JFPE - Página demorou para carregar. Tente reabrir.")
                    return True, None, None, True, False, False  # Show reopen interface
                
                # Check which element was found
                try:
                    avatar = driver.find_element(By.CLASS_NAME, "avatar")
                    print("[DEBUG] Already logged in - avatar found")
                except:
                    print("[DEBUG] Not logged in - proceeding with login")
                    # Need to login - use the iframe
                    sso_iframe = driver.find_element(By.ID, "ssoFrame")
                    driver.switch_to.frame(sso_iframe)
                    
                    time.sleep(3)
                    
                    # Check what's in the iframe
                    iframe_source = driver.page_source
                    
                    certificate_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "kc-pje-office"))
                    )

                    certificate_button.click()
            
                    driver.switch_to.default_content()
                    
                    WebDriverWait(driver, 15).until( 
                        EC.presence_of_element_located((By.CLASS_NAME, "avatar"))
                    )
            
            driver.get(search_url)
            
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
                # Use JavaScript click to avoid scrolling
                driver.execute_script("arguments[0].click();", search_button)
                
                # Wait for search results
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-link.btn-condensed"))
                )
                # Get the first result link
                first_result = driver.find_element(By.CSS_SELECTOR, ".btn-link.btn-condensed")
                
                # Click the result link to open the process page
                first_result.click()
                
                # Handle the confirmation alert that appears
                try:
                    # Wait for the alert to appear and accept it
                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()  # Click OK button
                    print("[DEBUG] Alert confirmed successfully")
                    
                    # Close the previous tab (search tab) after confirming alert
                    if len(driver.window_handles) > 1:
                        # Wait a moment for navigation to complete
                        time.sleep(2)
                        # Switch to the previous tab and close it safely
                        try:
                            previous_handle = driver.window_handles[-2] if len(driver.window_handles) > 1 else None
                            if previous_handle and self.safe_switch_to_window(driver, previous_handle):
                                self.safe_close_tab(driver)
                                # Switch back to the current process tab
                                self.safe_switch_to_last_window(driver)
                                print("[DEBUG] Previous tab closed successfully")
                        except Exception as tab_error:
                            print(f"[DEBUG] Error during tab cleanup: {tab_error}")
                        
                except TimeoutException:
                    print("[DEBUG] No alert appeared or alert timeout")
                except Exception as alert_error:
                    print(f"[DEBUG] Error handling alert: {alert_error}")
                    
            except Exception as parse_error:
                print(f"[DEBUG] Error parsing process number: {parse_error}")
                return False, None, None, False, True, True
            
            # Return success for Juizado (no further processing needed)
            return True, None, None, False, False, False
        except TimeoutException:
            notifier.show_toast("JFPE Login", "Timeout durante o login JFPE")
            return False, None, None, True, False, False #this is to show the reopen interface
        except Exception as e:
            print(f"[DEBUG] JFPE login error: {e}")
            notifier.show_toast("JFPE Login", f"Erro no login JFPE: {str(e)}")
            return False, None, None, True, False, False #this is to show the reopen interface

