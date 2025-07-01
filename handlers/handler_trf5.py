"""
TRF5 (Tribunal Regional Federal da 5ª Região) tribunal handler
"""
import tkinter as tk
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_handler import BaseTribunalHandler


class Trf5Handler(BaseTribunalHandler):
    
    def __init__(self):
        super().__init__("TRF5")
    
    def prompt_for_pje_level(self, paste):
        """
        Prompt user to choose PJE level for TRF5 processes.
        """
        # Extract the first 2 digits of the final 4 digits to determine the specific tribunal
        try:
            parts = paste.split('-')[1].split('.')
            final_digits = parts[4] if len(parts) >= 5 else None
            # Get first 2 digits for tribunal determination (e.g., "80" from "8000", "82" from "8200")
            first_two_digits = final_digits[:2] if final_digits and len(final_digits) >= 2 else None
            print(f"[DEBUG] Final digits for UI: {final_digits}, First 2: {first_two_digits}")
        except:
            final_digits = None
            first_two_digits = None
            print("[DEBUG] Could not extract final digits for UI")

        # Determine tribunal name and create appropriate window title
        tribunal_name = "TRF5"
        if first_two_digits == "80":
            tribunal_name = "JFAL"
        elif first_two_digits == "81":
            tribunal_name = "JFCE"
        elif first_two_digits == "82":
            tribunal_name = "JFPB"
        elif first_two_digits == "83":
            tribunal_name = "JFPE"
        elif first_two_digits == "84":
            tribunal_name = "JFRN"
        elif first_two_digits == "85":
            tribunal_name = "JFSE"

        window_title = f"Escolha o Grau - {tribunal_name}"
        pje_level_window, font_style = self.create_prompt_window(window_title, paste, 400)
        
        pje_level = tk.StringVar(value="")

        def select_level(level):
            pje_level.set(level)
            pje_level_window.destroy()

        # Add common buttons (always shown)
        self.add_button(pje_level_window, "Juizado Primeiro grau", lambda: select_level("Juizado Primeiro grau"), font_style)
        self.add_button(pje_level_window, "Juizado Turma Recursal", lambda: select_level("Juizado Turma Recursal"), font_style)
        
        # Add specific tribunal buttons based on first 2 digits
        if first_two_digits:
            if first_two_digits == "80":  # JFAL
                self.add_button(pje_level_window, "JFAL - Advogado 1G", lambda: select_level("JFAL - Advogado"), font_style)
                self.add_button(pje_level_window, "JFAL - Terceiros 1G", lambda: select_level("JFAL - Terceiros"), font_style)
            elif first_two_digits == "81":  # JFCE
                self.add_button(pje_level_window, "JFCE - Advogado 1G", lambda: select_level("JFCE - Advogado"), font_style)
                self.add_button(pje_level_window, "JFCE - Terceiros 1G", lambda: select_level("JFCE - Terceiros"), font_style)
            elif first_two_digits == "82":  # JFPB
                self.add_button(pje_level_window, "JFPB - Advogado 1G", lambda: select_level("JFPB - Advogado"), font_style)
                self.add_button(pje_level_window, "JFPB - Terceiros 1G", lambda: select_level("JFPB - Terceiros"), font_style)
            elif first_two_digits == "83":  # JFPE
                self.add_button(pje_level_window, "JFPE - Advogado 1G", lambda: select_level("JFPE - Advogado"), font_style)
                self.add_button(pje_level_window, "JFPE - Terceiros 1G", lambda: select_level("JFPE - Terceiros"), font_style)
            elif first_two_digits == "84":  # JFRN
                self.add_button(pje_level_window, "JFRN - Advogado 1G", lambda: select_level("JFRN - Advogado"), font_style)
                self.add_button(pje_level_window, "JFRN - Terceiros 1G", lambda: select_level("JFRN - Terceiros"), font_style)
            elif first_two_digits == "85":  # JFSE
                self.add_button(pje_level_window, "JFSE - Advogado 1G", lambda: select_level("JFSE - Advogado"), font_style)
                self.add_button(pje_level_window, "JFSE - Terceiros 1G", lambda: select_level("JFSE - Terceiros"), font_style)
        else:
            # Fallback: show generic options if we can't determine the tribunal
            self.add_button(pje_level_window, "JF - Advogado 1G", lambda: select_level("JF - Advogado"), font_style)
            self.add_button(pje_level_window, "JF - Terceiros 1G", lambda: select_level("JF - Terceiros"), font_style)

        # Add TRF5 2G common options (always available)
        self.add_button(pje_level_window, "TRF5 - Advogado 2G", lambda: select_level("TRF5 - Advogado"), font_style)
        self.add_button(pje_level_window, "TRF5 - Terceiros 2G", lambda: select_level("TRF5 - Terceiros"), font_style)
        
        # Add ignore button
        self.add_ignore_button(pje_level_window, pje_level, font_style)

        pje_level_window.mainloop()
        return pje_level.get()
    
    def handle_login(self, driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
        # Extract the first 2 digits of the final 4 digits to determine the specific tribunal
        try:
            # Get the final 4 digits from the process number
            parts = paste.split('-')[1].split('.')
            final_digits = parts[4] if len(parts) >= 5 else None
            # Get first 2 digits for tribunal determination (e.g., "80" from "8000", "82" from "8200")
            first_two_digits = final_digits[:2] if final_digits and len(final_digits) >= 2 else None
            print(f"[DEBUG] Final digits: {final_digits}, First 2: {first_two_digits}")
        except:
            final_digits = None
            first_two_digits = None
            print("[DEBUG] Could not extract final digits")

        # Determine URLs based on PJE level
        if pje_level == "Juizado Primeiro grau":
            base_url = "https://pje1g.trf5.jus.br/pje/login.seam"
            search_url = "https://pje1g.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
        
        elif pje_level == "Juizado Turma Recursal":
            base_url = "https://pje2g.trf5.jus.br/pje/login.seam"
            search_url = "https://pje2g.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
        
        # TRF5 2G (Common for all tribunals)
        elif pje_level == "TRF5 - Advogado":
            base_url = "https://pje.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            search_url = "https://pje.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
        
        elif pje_level == "TRF5 - Terceiros":
            base_url = "https://pje.trf5.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            search_url = "https://pje.trf5.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
        
        # Individual tribunal URLs based on first 2 digits
        elif pje_level in ["JFAL - Advogado", "JFCE - Advogado", "JFPB - Advogado", "JFPE - Advogado", "JFRN - Advogado", "JFSE - Advogado", "JF - Advogado"]:
            # Determine the specific domain based on first 2 digits
            if first_two_digits == "80":  # JFAL
                base_url = "https://pje.jfal.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            elif first_two_digits == "81":  # JFCE
                base_url = "https://pje.jfce.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            elif first_two_digits == "82":  # JFPB
                base_url = "https://pje.jfpb.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            elif first_two_digits == "83":  # JFPE
                base_url = "https://pje.jfpe.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            elif first_two_digits == "84":  # JFRN
                base_url = "https://pje.jfrn.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            elif first_two_digits == "85":  # JFSE
                base_url = "https://pje.jfse.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            else:
                # Fallback to TRF5 if first 2 digits don't match
                base_url = "https://pje.trf5.jus.br/pje/Processo/ConsultaProcesso/listView.seam"
            search_url = base_url
        
        elif pje_level in ["JFAL - Terceiros", "JFCE - Terceiros", "JFPB - Terceiros", "JFPE - Terceiros", "JFRN - Terceiros", "JFSE - Terceiros", "JF - Terceiros"]:
            # Determine the specific domain based on first 2 digits
            if first_two_digits == "80":  # JFAL
                base_url = "https://pje.jfal.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            elif first_two_digits == "81":  # JFCE
                base_url = "https://pje.jfce.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            elif first_two_digits == "82":  # JFPB
                base_url = "https://pje.jfpb.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            elif first_two_digits == "83":  # JFPE
                base_url = "https://pje.jfpe.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            elif first_two_digits == "84":  # JFRN
                base_url = "https://pje.jfrn.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            elif first_two_digits == "85":  # JFSE
                base_url = "https://pje.jfse.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            else:
                # Fallback to TRF5 if first 2 digits don't match
                base_url = "https://pje.trf5.jus.br/pje/Processo/ConsultaProcessoTerceiros/listView.seam"
            search_url = base_url
        
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

            # Different login flow for Justiça Federal (all individual tribunals and TRF5)
            if pje_level in ["JFAL - Advogado", "JFAL - Terceiros", "JFCE - Advogado", "JFCE - Terceiros", 
                           "JFPB - Advogado", "JFPB - Terceiros", "JFPE - Advogado", "JFPE - Terceiros",
                           "JFRN - Advogado", "JFRN - Terceiros", "JFSE - Advogado", "JFSE - Terceiros",
                           "TRF5 - Advogado", "TRF5 - Terceiros", "JF - Advogado", "JF - Terceiros"]:
                try:
                    login_element = WebDriverWait(driver, 20).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.ID, "nomeUsuario")),
                            EC.presence_of_element_located((By.ID, "loginAplicacaoButton"))
                        )
                    )
                except TimeoutException:
                    print("[DEBUG] Page took too long to load - showing reopen interface")
                    return True, None, None, True, False, True  # Show reopen interface
                
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
                            utilizar_btn = WebDriverWait(driver, 10).until(
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
                                login_button = WebDriverWait(driver, 20).until(
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
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.ID, "nomeUsuario"))
                        )
                        print("[DEBUG] Login form loaded - password field (nomeUsuario) found")
                        
                    except TimeoutException:
                        print("[DEBUG] Timeout waiting for login elements in Justiça Federal Comum")
                        notifier.send("TRF5 - Timeout ao carregar login da Justiça Federal Comum")
                        return True, None, None, True, False, False
                
                # Navigate to search URL and fill the form
                driver.get(search_url)
                
                if pje_level in ["JFAL - Advogado", "JFCE - Advogado", "JFPB - Advogado", "JFPE - Advogado", 
                               "JFRN - Advogado", "JFSE - Advogado", "TRF5 - Advogado", "JF - Advogado"]:
                    # Normal consultation for lawyers/registered users
                    try:
                        # Wait for the search form to load
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.ID, "consultarProcessoForm:numeroProcessoDecoration:numeroProcesso"))
                        )
                        
                        # Fill the process number field
                        process_field = driver.find_element(By.ID, "consultarProcessoForm:numeroProcessoDecoration:numeroProcesso")
                        
                        print(f"[DEBUG] Sending keys to normal consultation field: '{paste}'")
                        
                        # Clear and fill the field
                        process_field.clear()
                        process_field.click()
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].setSelectionRange(0, 0);", process_field)
                        driver.execute_script("arguments[0].focus();", process_field)
                        process_field.send_keys(paste)
                        time.sleep(1)
                        
                        # Click the search button
                        search_button = driver.find_element(By.ID, "consultarProcessoForm:searchButton")
                        search_button.click()

                        # Wait for search results and extract the process details URL
                        print("[DEBUG] Waiting for normal consultation results...")
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".rich-table-row.rich-table-firstrow"))
                        )
                        
                        # Find the "Ver Detalhes" image in the first row
                        ver_detalhes_img = driver.find_element(By.CSS_SELECTOR, "img[title='Ver Detalhes']")
                        ver_detalhes_img.click()
                        
                    
                            
                    except Exception as normal_error:
                        print(f"[DEBUG] Normal consultation failed: {normal_error}")
                        return False, None, None, False, True, True
                
                elif pje_level in ["JFAL - Terceiros", "JFCE - Terceiros", "JFPB - Terceiros", "JFPE - Terceiros",
                                 "JFRN - Terceiros", "JFSE - Terceiros", "TRF5 - Terceiros", "JF - Terceiros"]:
                    # Third-party consultation for non-registered users
                    try:
                        # Wait for the third-party search form to load
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.ID, "pesquisarProcessoTerceiroForm:nrProcessoDecoration:nrProcesso"))
                        )
                        
                        # Fill the process number field for third-party consultation
                        terceiros_field = driver.find_element(By.ID, "pesquisarProcessoTerceiroForm:nrProcessoDecoration:nrProcesso")
                        
                        print(f"[DEBUG] Sending keys to third-party consultation field: '{paste}'")
                        
                        terceiros_field.clear()
                        terceiros_field.click()
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].setSelectionRange(0, 0);", terceiros_field)
                        driver.execute_script("arguments[0].focus();", terceiros_field)
                        terceiros_field.send_keys(paste)
                        time.sleep(1)
                        
                        # Click the third-party search button
                        terceiros_search_button = driver.find_element(By.ID, "pesquisarProcessoTerceiroForm:searchButton")
                        terceiros_search_button.click()
                        
                        # Wait for search results
                        print("[DEBUG] Waiting for third-party consultation results...")
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "img[title='Ver Detalhe']"))
                        )
                        
                        # Click the "Ver Detalhe" link to open popup
                        ver_detalhe_img = driver.find_element(By.CSS_SELECTOR, "img[title='Ver Detalhe']")
                        ver_detalhe_img.click()
                        
                        print("[DEBUG] Clicked 'Ver Detalhe' - popup should open")
                        
                        # Wait for the popup to appear
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "modal:motivacaoDecoration:motivacao"))
                        )
                        
                        print("[DEBUG] Motivation popup appeared")
                        
                        # Fill the motivation field with "Consulta"
                        try:
                            # Wait for the textarea to be visible and interactable
                            motivation_field = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.ID, "modal:motivacaoDecoration:motivacao"))
                            )
                            
                            # Focus on the field first
                            driver.execute_script("arguments[0].focus();", motivation_field)
                            time.sleep(0.5)
                            
                            # Clear and fill with JavaScript to ensure it works
                            driver.execute_script("arguments[0].value = '';", motivation_field)
                            driver.execute_script("arguments[0].value = 'Consulta';", motivation_field)
                            
                            # Trigger events to ensure validation passes
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", motivation_field)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", motivation_field)
                            
                            print("[DEBUG] Motivation field filled with 'Consulta' using JavaScript")
                            
                            # Wait a moment for any validation
                            time.sleep(1)
                            
                            # Click the Gravar button with JavaScript to avoid interaction issues
                            gravar_button = driver.find_element(By.ID, "modal:btnGravar")
                            driver.execute_script("arguments[0].click();", gravar_button)
                            print("[DEBUG] Clicked Gravar button using JavaScript")
                            
                            # Wait for the popup to close and process page to load
                            time.sleep(5)
                            print("[DEBUG] Third-party consultation completed successfully")
                            
                        except Exception as motivation_error:
                            print(f"[DEBUG] Error filling motivation or clicking Gravar: {motivation_error}")
                            return False, None, None, False, True, True
                        except Exception as button_error:
                            print(f"[DEBUG] Error accessing Gravar button: {button_error}")
                            return False, None, None, False, True, True
                            
                    except Exception as terceiros_error:
                        print(f"[DEBUG] Third-party consultation failed: {terceiros_error}")
                        return False, None, None, False, True, True
                
                # Return success for Justiça Federal Comum (no further processing needed)
                return True, None, None, False, False, False

            ######JUIZADO PRIMEIRO GRAU OR TURMA RECUSAL########   
            else:
                try:
                    login_element = WebDriverWait(driver, 20).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CLASS_NAME, "avatar")),
                            EC.presence_of_element_located((By.ID, "ssoFrame"))
                        )
                    )
                except TimeoutException:
                    print("[DEBUG] Page took too long to load - showing reopen interface")
                    return True, None, None, True, False, True  # Show reopen interface
                
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
                    
                    certificate_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.ID, "kc-pje-office"))
                    )

                    certificate_button.click()
            
                    driver.switch_to.default_content()
                    
                    WebDriverWait(driver, 20).until( 
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
                    WebDriverWait(driver, 10).until(EC.alert_is_present())
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
            notifier.show_toast("TRF5 Login", "Timeout durante o login TRF5")
            return False, None, None, True, False, False #this is to show the reopen interface
        except Exception as e:
            print(f"[DEBUG] TRF5 login error: {e}")
            notifier.show_toast("TRF5 Login", f"Erro no login TRF5: {str(e)}")
            return False, None, None, True, False, False #this is to show the reopen interface
