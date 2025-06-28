"""
Base handler class for tribunal-specific logic
"""
import tkinter as tk
import time
import os
import sys
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Icon path setup
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.dirname(__file__))

ICON_PATH = os.path.join(BASE_PATH, "icon.ico")
TKINTER_ICON_PATH = ICON_PATH


class BaseTribunalHandler:
    """
    Base class for tribunal handlers providing common functionality.
    """
    
    def __init__(self, tribunal_name):
        self.tribunal_name = tribunal_name
    
    def prompt_for_pje_level(self, paste):
        """
        Abstract method to be implemented by each tribunal handler.
        Should return the selected PJE level.
        """
        raise NotImplementedError("Must be implemented by subclass")
    
    def handle_login(self, driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
        """
        Abstract method to be implemented by each tribunal handler.
        Returns: (success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
        """
        raise NotImplementedError("Must be implemented by subclass")
    
    def fetch_process_id(self, driver, id_url):
        """
        Fetch process ID from the PJE API.
        Common implementation shared by all tribunals.
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
    
    def perform_pje_login(self, driver, base_url, usuario_pje, senha_pje, login_method):
        """
        Perform the actual PJE login process.
        Common implementation that can be customized per tribunal if needed.
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
    
    def create_prompt_window(self, title, paste, window_height=300):
        """
        Create the base tkinter window for PJE level selection.
        """
        pje_level_window = tk.Tk()
        pje_level_window.title(title)
        pje_level_window.attributes('-topmost', True)
        pje_level_window.configure(bg="#D9CDFF")

        # Set custom icon for the tkinter window
        pje_level_window.iconbitmap(TKINTER_ICON_PATH)

        screen_width = pje_level_window.winfo_screenwidth()
        screen_height = pje_level_window.winfo_screenheight()
        window_width = 300
        position_right = screen_width - window_width - 20
        position_down = screen_height - window_height - 80
        pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        font_style = ("Montserrat", 12)

        # Create the label with process information
        label_text = f"Detectado processo {self.tribunal_name}\n{paste}" if hasattr(self, 'tribunal_name') else f"Detectado o processo\n{paste}"
        tk.Label(pje_level_window, text=label_text, bg="#D9CDFF", fg="#484554", font=(font_style[0], font_style[1], "bold")).pack(pady=10)

        return pje_level_window, font_style
    
    def add_button(self, window, text, command, font_style, bg_color="#A084E8", fg_color="#FFFFFF"):
        """
        Add a button to the prompt window.
        """
        tk.Button(window, text=text, command=command, bg=bg_color, fg=fg_color, width=20, font=font_style).pack(pady=5)
    
    def add_ignore_button(self, window, pje_level_var, font_style):
        """
        Add the ignore button (common to all tribunals).
        """
        def select_ignore():
            pje_level_var.set("Ignore")
            window.destroy()
        
        self.add_button(window, "Ignorar e aguardar", select_ignore, font_style, "#CFCBE7", "#3F3D56")
        
        def on_close():
            pje_level_var.set("Ignore")
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_close)
