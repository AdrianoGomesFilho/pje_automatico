import psutil
import os
import sys 
import time
import threading
import requests  # Add this import for HTTP requests
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from tkinter import PhotoImage
import tkinter as tk  # Ensure tkinter is imported as tk
from cryptography.fernet import Fernet
import pyperclip  # Ensure pyperclip is imported
import tkinter.messagebox as messagebox  # Import messagebox for alerts
from plyer import notification
from selenium.common.exceptions import NoSuchElementException
from win10toast import ToastNotifier  # Add this import for Windows notifications

CURRENT_VERSION = "1.1.1"

UPDATE_URL = "https://raw.githubusercontent.com/AdrianoGomesFilho/pje_automatico/main/latest_version.json"

SITE_PJE_AUTOMATICO = "https://pje-automatico.vercel.app/"

if getattr(sys, 'frozen', False): #diferencia se o programa está rodando como .exe ou não
    BASE_PATH = sys._MEIPASS #meipass é o diretório temporário onde o PyInstaller extrai os arquivos
    print(f"Running in frozen mode (executable). Base path: {BASE_PATH}")
else:
    BASE_PATH = os.path.dirname(__file__) #o próprio diretório do script
    print(f"Running in normal mode (script). Base path: {BASE_PATH}") 

ICON_PATH = os.path.join(BASE_PATH, "icon.ico")
LOGO_PATH = os.path.join(BASE_PATH, "logowide.png")

TKINTER_ICON_PATH = ICON_PATH
PYSTRAY_ICON_PATH = ICON_PATH

def check_for_updates():
    try:
        print("Checking for updates...")
        response = requests.get(UPDATE_URL, timeout=10)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        try:
            update_info = response.json()
            print(f"Update info received: {update_info}") 
        except ValueError:
            print("Erro: Resposta do servidor não é um JSON válido.")
            return

        latest_version = update_info.get("version")
        releases_page_url = update_info.get("download_url")
        print(f"Latest version: {latest_version}, Current version: {CURRENT_VERSION}")

        if latest_version and latest_version != CURRENT_VERSION:
            print("New version available. Prompting user...") 
            alert_window = tk.Tk() #cria uma nova janela
            alert_window.title("Atualização Disponível")
            alert_window.attributes('-topmost', True)
            alert_window.configure(bg="#ECE9FD")

            # Set custom icon for the tkinter window
            alert_window.iconbitmap(TKINTER_ICON_PATH)

            screen_width = alert_window.winfo_screenwidth()
            screen_height = alert_window.winfo_screenheight()
            window_width = 400
            window_height = 250
            position_right = int(screen_width / 2 - window_width / 2)
            position_down = int(screen_height / 2 - window_height / 2)
            alert_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

            font_style = ("Montserrat", 12)

            tk.Label(alert_window, text="Nova versão disponível!", bg="#ECE9FD", fg="#3F3D56", font=("Montserrat", 14, "bold")).pack(pady=10)
            tk.Label(alert_window, text=f"Versão: {latest_version}", bg="#ECE9FD", fg="#3F3D56", font=font_style).pack(pady=5)

            def open_pje_automatico_site():
                import webbrowser
                webbrowser.open(SITE_PJE_AUTOMATICO)
                alert_window.destroy()  # Close the current window
                sys.exit(0)

            tk.Button(alert_window, text="Ir para download", command=open_pje_automatico_site, bg="#A084E8", fg="#FFFFFF", font=font_style, width=25).pack(pady=5)

            def close_window():
                alert_window.destroy()

            tk.Button(alert_window, text="Continuar com a versão atual", command=close_window, bg="#CFCBE7", fg="#3F3D56", font=font_style, width=25).pack(pady=5)

            def close_program():
                alert_window.destroy()
                sys.exit(0)

            # Handle the close (X) button
            alert_window.protocol("WM_DELETE_WINDOW", close_program)

            tk.Button(alert_window, text="Fechar", command=close_program, bg="#CFCBE7", fg="#3F3D56", font=font_style, width=20).pack(pady=5)

            alert_window.mainloop()
        else:
            print("Nenhuma atualização disponível.")
    except Exception as e:
        print(f"Falha ao verificar atualizações: {e}")

# Verifica atualizações antes de iniciar o script principal
check_for_updates()

# Dynamically determine the process name based on the executable file
PROCESS_NAME = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "pje_automatico.py"

# Find and kill any running instance of the process
for proc in psutil.process_iter(['pid', 'name']): # loop that iterates over processes
    if proc.info['name'] == PROCESS_NAME and proc.pid != os.getpid():
        print(f"Closing old instance (PID: {proc.pid})...")
        proc.terminate()  # Try to terminate gracefully
        time.sleep(1)  # Wait a bit for the process to close
        if proc.is_running():
            proc.kill()  # Force kill if still running
        print("Old instance closed.")

# Continue with the new instance
print("Starting new instance...")

import time
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

# Function to create a custom icon for the system tray
def create_image():
    image = Image.open(PYSTRAY_ICON_PATH)
    return image

# Store recent processes in a list
recent_processes = []

# Function to add a process to the recent list
def add_to_recent(process):
    """
    Add a process to the recent list, ensuring the last opened process is always at the top.
    """
    global recent_processes, tray_icon
    if process in recent_processes:
        recent_processes.remove(process)  # Remove the process if it already exists
    recent_processes.insert(0, process)  # Add the process to the top of the list
    if len(recent_processes) > 20:  # Limit the list to 20 items
        recent_processes.pop()  # Remove the oldest item
    # Update the tray menu dynamically
    tray_icon.menu = create_menu()

def set_bypass_repeated_content():
    """
    Set the bypass_repeated_content variable to True to allow reopening the same process.
    """
    global bypass_repeated_content
    bypass_repeated_content = True

def create_menu():
    """
    Create the system tray menu with a title and recent processes.
    """
    global bypass_repeated_content  # Ensure we can modify the global variable

    # Add a title to the menu
    menu_items = [
        MenuItem("Processos recentes detectados (clique para reabrir)", lambda: None, enabled=False)  # Title as a disabled item
    ]

    # Add recent processes to the menu
    menu_items.extend(
        MenuItem(
            str(process),
            lambda item, p=process: (pyperclip.copy(str(p)), set_bypass_repeated_content())
        ) for process in recent_processes
    )

    return Menu(*menu_items)

def run_tray_icon():
    """
    Run the system tray icon with left-click access.
    """
    global tray_icon
    tray_icon = Icon("PJE Script", create_image(), "PJE Automático", create_menu())

    # Enable left-click access to the menu
    tray_icon.menu = create_menu()
    tray_icon.run()

# Start the tray icon in a separate thread
tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
tray_thread.start()

# Function to create a custom icon for the taskbar
def create_taskbar_icon():
    return Image.open(ICON_PATH)

# Function to set the taskbar icon
def set_taskbar_icon():
    """
    Set a custom icon for the taskbar.
    """
    from ctypes import windll
    import win32gui
    import win32con

    hwnd = win32gui.GetForegroundWindow()  # Get the current window handle
    hicon = windll.user32.LoadImageW(0, ICON_PATH, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE)
    if hicon:
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon)
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, hicon)

# Initialize the taskbar icon
taskbar_icon = set_taskbar_icon()

# Ensure the icon is removed when the application exits
import atexit
if taskbar_icon:
    atexit.register(lambda: taskbar_icon.stop() if hasattr(taskbar_icon, 'stop') else None)

# Define color variables
BACKGROUND_COLOR = "#ECE9FD"  # Very light lavender, soft background
TEXT_COLOR = "#3F3D56"        # Deep gray-purple, strong contrast for readability
BUTTON_BG_COLOR = "#A084E8"   # Soft purple, eye-catching and on-theme
BUTTON_FG_COLOR = "#FFFFFF"   # White, clean text on button
DISABLED_BUTTON_BG_COLOR = "#CFCBE7"  # Muted lavender-gray, subtle disabled state
LINK_COLOR = "#7B6EF6"        # Vivid purple-blue, good for links   

# Function to open the initial tab
def open_initial_tab(driver):
    """
    Open the specified site in the browser.
    """
    driver.get("https://pje-automatico.vercel.app/")

# Define the monitor_browser function first
def monitor_browser(driver):
    """
    Monitor the browser and exit the program if the browser is closed or an error occurs.
    """
    while True:
        try:
            # Check if there are any open tabs
            if len(driver.window_handles) == 0:
                print("No tabs open. Exiting program...")
                notifier.send("O PJE Automático foi encerrado")  # Notify the user before exiting
                time.sleep(1)  # Wait a bit before retrying
                driver.quit()  # Close the browser
                os._exit(0)  # Exit the program
            time.sleep(1)  # Check periodically
        except Exception as e:
            print(f"Error in monitor_browser: {e}")
            notifier.send("O PJE Automático foi encerrado.")  # Notify the user
            driver.quit()  # Close the browser
            os._exit(0)  # Exit the program

def remove_cdk_overlay(driver):
    """
    Continuously monitor the page for the 'cdk-overlay-container' element and remove it from the DOM 
    if any of its children contain the text 'A página será fechada'.
    """
    while True:
        try:
            driver.execute_script("""
//                const overlay = document.querySelector('.cdk-overlay-container');
//                if (overlay) {
//                    const containsText = Array.from(overlay.querySelectorAll('*')).some(el => 
//                        el.textContent.includes('A página será fechada')
//                    );
//                    if (containsText) {
//                        overlay.remove();
//                        console.log('Removed cdk-overlay-container from DOM.');
//                    }
//                }
            """)
            time.sleep(1)  # Check periodically
        except Exception as e:
            if "no such window" in str(e) or "web view not found" in str(e):
                print("Window already closed. Continuing execution...")
                break
            else:
                print(f"Error while removing cdk-overlay-container: {e}")
                break


# Function to run the main script
def run_script(credentials):
    global usuario_pje, senha_pje, usuario_astrea, senha_astrea, login_method, pje_level, bypass_repeated_content
    bypass_repeated_content = False  # Initialize the variable

    usuario_pje = credentials["USERNAMEPJE"]
    senha_pje = credentials["PASSWORDPJE"]
    usuario_astrea = credentials["USERNAMEASTREA"]
    senha_astrea = credentials["PASSWORDASTREA"]
    login_method = credentials["LOGIN_METHOD"]

    print(f"CPF para login no PDPJ: {usuario_pje}")
    print(f"Senha para login no PDPJ: xxxxxxxxxxxx")
    print(f"E-mail do Astrea: {usuario_astrea}")
    print(f"Senha do Astrea: xxxxxxxxxxxx")
    print(f"Método de login: {login_method}")

    # Specify the path to your Chrome user data directory
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
    chrome_options.add_argument("--start-maximized")  # Open browser in fullscreen

    # Declare browser_process_id as a global variable and initialize it
    global browser_process_id
    browser_process_id = None

    # Enhanced function to check if the browser process is running
    def is_browser_running():
        global browser_process_id
        if browser_process_id is None:
            return False
        try:
            # Check if the process with the stored ID is still running and is a browser
            process = psutil.Process(browser_process_id)
            if "chrome" in process.name().lower():
                return True
        except psutil.NoSuchProcess:
            pass
        return False

    # Function to close any existing browser instances associated with the application
    def close_existing_browser_instances():
        print("[INFO] Checking for existing browser instances...")
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if the process is a browser (e.g., Chrome) and was launched by this application
                if "chrome" in proc.info['name'].lower() and proc.info['cmdline'] and any("--remote-debugging-port" in cmd for cmd in proc.info['cmdline']):
                    print(f"[INFO] Found browser instance: PID={proc.pid}. Closing...")
                    proc.terminate()  # Try to terminate gracefully
                    time.sleep(1)  # Wait a bit for the process to close
                    if proc.is_running():
                        print(f"[WARNING] Process PID={proc.pid} still running. Forcing kill...")
                        proc.kill()  # Force kill if still running
                    print(f"[INFO] Successfully closed browser instance: PID={proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    # Call the function to close existing browser instances
    close_existing_browser_instances()

    # Update the browser launch logic
    if not is_browser_running():
        print("No existing browser instance detected. Launching a new browser...")
        # Initialize WebDriver with Chrome options
        driver = webdriver.Chrome(options=chrome_options)

        # Store the browser process ID
        browser_process_id = driver.service.process.pid

        # Open the initial tab
        open_initial_tab(driver)

        # Start a thread to monitor the browser
        browser_monitor_thread = threading.Thread(target=monitor_browser, args=(driver,), daemon=True)
        browser_monitor_thread.start()

        # Start a thread to monitor and remove 'cdk-overlay-container'
        overlay_removal_thread = threading.Thread(target=remove_cdk_overlay, args=(driver,), daemon=True)
        overlay_removal_thread.start()
    else:
        print("Browser is already running. Avoiding duplicate instance.")

    # Store the last clipboard content
    last_clipboard_content = ""

    def fetch_process_id(driver, id_url):
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

    try:
        while True:
            try:
                paste = pyperclip.paste().replace(" ", "").strip()  # Remove all spaces and leading/trailing whitespace
                pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')

                # Check if the clipboard content is new or bypassing is enabled
                if bypass_repeated_content or (paste != last_clipboard_content and pattern.fullmatch(paste)):
                    print(f"Processo identificado: {paste}")
                    add_to_recent(paste)  # Add the detected process to the recent list

                    # Debugging: Log the current state of window handles
                    print(f"[DEBUG] Current window handles: {driver.window_handles}")

                    # Reset the state if tabs are closed or WebDriver loses connection
                    if not driver.window_handles:  # Check if the list is empty
                        print("[DEBUG] No tabs detected (driver.window_handles is empty). Resetting state...")
                        last_clipboard_content = ""  # Clear the last clipboard content
                        bypass_repeated_content = False  # Reset bypass flag
                        try:
                            # Attempt to open a new tab to recover
                            driver.execute_script("window.open('about:blank', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])
                            print("[DEBUG] Recovered by opening a new tab.")
                        except Exception as recovery_error:
                            print(f"[ERROR] Failed to recover WebDriver state: {recovery_error}")
                            break  # Exit the loop if recovery fails
                        continue  # Wait for new clipboard content

                    # Ensure the current tab is valid
                    try:
                        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                        driver.current_url  # Validate the current tab
                    except Exception as e:
                        print(f"[DEBUG] Current tab is invalid: {e}. Opening a new tab...")
                        driver.execute_script("window.open('about:blank', '_blank');")
                        driver.switch_to.window(driver.window_handles[-1])

                    # Process the new clipboard content
                    last_clipboard_content = paste  # Update the last clipboard content
                    bypass_repeated_content = False  # Reset bypass flag after processing
                    processo_nao_cadastrado = False

                    #########################ASTREA######################################

                    if login_method in ["Astrea + PJE (login PDPJ CPF e Senha)", "Astrea", "Astrea + PJE (Token)"]:
                        # Perform Astrea login and other actions
                        astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"
                        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                        driver.execute_script(f"window.open('{astrea_url}', '_blank');")
                        astrea_handle = driver.window_handles[-1]
                        driver.switch_to.window(astrea_handle)

                        try:
                            # Wait for either the 'search' element or the 'submit' button to appear
                            element_present = WebDriverWait(driver, 25).until(
                                EC.any_of(
                                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Digite seu email']")),
                                    EC.presence_of_element_located((By.ID, "search"))
                                )
                            )

                            if element_present.get_attribute("id") == "search":
                                print("Element with ID 'search' is present. Proceeding to open PJE.")
                                # Proceed to open PJE
                                # ...existing code to open PJE...
                            else:
                                print("Login form is present. Performing login.")
                                # Credentials
                                username_field = driver.find_element(By.NAME, "username")
                                password_field = driver.find_element(By.NAME, "password")

                                username_field.send_keys(usuario_astrea)
                                password_field.send_keys(senha_astrea)

                                # Submit the login form
                                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                                login_button.click()
                                print("Login realizado. Proceeding to open PJE.")
                                # Proceed to open PJE after login
                                # ...existing code to open PJE...
                        except TimeoutException:
                            print("Neither 'search' element nor 'submit' button found. Unable to proceed.")
                    else:
                        print("Já logado Astrea ou ignorando login Astrea (método).")

            
                    while True:
                        trt_number = paste[18:20]
                        trt_number = trt_number.lstrip('0')

                        # Prompt user to choose the PJE level
                        pje_level = prompt_for_pje_level(paste)

                        if pje_level == "Ignore":
                            print("Opção ignorada. Aguardando novo conteúdo na área de transferência.")
                            break  # Exit the loop and wait for new clipboard content

                        if pje_level == "Primeiro grau PJE":
                            base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
                            id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                        elif pje_level == "Segundo grau PJE":
                            base_url = f"https://pje.trt{trt_number}.jus.br/segundograu/login.seam"
                            id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                        elif pje_level == "TST PJE":
                            base_url = "https://pje.tst.jus.br/tst/login.seam"
                            id_url = f"https://pje.tst.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}" 
                        elif pje_level == "TST Antigo":
                            paste_parts = paste.split('-')
                            numeroTst = paste_parts[0]
                            remaining_parts = paste_parts[1].split('.')
                            digitoTst = remaining_parts[0]
                            anoTst = remaining_parts[1]
                            orgaoTst = remaining_parts[2]
                            tribunalTst = remaining_parts[3]
                            varaTst = remaining_parts[4]

                            base_url = f"https://consultaprocessual.tst.jus.br/consultaProcessual/consultaTstNumUnica.do?conscsjt=&numeroTst={numeroTst}&digitoTst={digitoTst}&anoTst={anoTst}&orgaoTst={orgaoTst}&tribunalTst={tribunalTst}&varaTst={varaTst}&consulta=Consultar"

                        
                        if pje_level == "TST Antigo":
                            driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                            driver.execute_script(f"window.open('{base_url}', '_blank');")
                            time.sleep(3)
                            notifier.send("TST Antigo - Caso esteja em consulta de terceiros, tente reabrir com a opcão 'TST PJE'")
                            break
                        else:
                            driver.execute_script(f"window.open('{base_url}', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
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

                                # Wait for either "botao-certificado-titulo" or "brasao-republica" to be present
                                elemento_login = wait_for_any_element(driver, [
                                    (By.ID, "kc-login"),
                                    (By.ID, "brasao-republica"),
                                    (By.ID, "formPesquisa")
                                ])

                                if elemento_login.get_attribute("ID") == "kc-login":
                                    if login_method in ["4", "2"]:
                                        driver.find_element(By.CLASS_NAME, "botao-certificado-titulo").click()
                                        elemento_login = WebDriverWait(driver, 30).until(
                                            EC.presence_of_element_located((By.ID, "brasao-republica")) or
                                            EC.presence_of_element_located((By.ID, "formPesquisa"))
                                        )
                                        process_id = fetch_process_id(driver, id_url)
                                    else:
                                        driver.find_element(By.ID, "username").send_keys(usuario_pje)
                                        driver.find_element(By.ID, "password").send_keys(senha_pje)
                                        driver.find_element(By.ID, "kc-login").click()
                                        elemento_login = WebDriverWait(driver, 30).until(
                                            EC.presence_of_element_located((By.ID, "brasao-republica")) or ##intencional debugging
                                            EC.presence_of_element_located((By.ID, "formPesquisa")) ##intencional debugging
                                        )
                                        process_id = fetch_process_id(driver, id_url)
                                elif elemento_login.get_attribute("id") in ["brasao-republica", "formPesquisa"]:
                                    process_id = fetch_process_id(driver, id_url)
                            except (ValueError, TimeoutException):
                                bypass_repeated_content = True  # Enable bypass for repeated content
                                processo_nao_cadastrado = True
                                break  # Exit the loop and reopen the PJE level prompt
                            else:
                                break  # Exit the loop if process_id is successfully fetched
                    if pje_level != "TST Antigo":
                        if processo_nao_cadastrado:
                            reopen_choice = prompt_reopen_pje(paste)
                            if reopen_choice:
                                bypass_repeated_content = True  # Enable bypass for repeated content
                                continue  # Reopen the PJE level prompt
                            else:
                                print(f"Opção ignorada para o processo {paste}. Aguardando novo conteúdo na área de transferência.")
                                bypass_repeated_content = False
                                continue  # Continue monitoring clipboard content
                        else:
                                # Construct the final_url using the fetched id
                            if pje_level == "Ignore":
                                print("Opção ignorada. Aguardando novo conteúdo na área de transferência.")
                                continue  # Skip processing and wait for new clipboard content
                            elif pje_level == "TST PJE":
                                final_url = f"https://pje.tst.jus.br/pjekz/processo/{process_id}/detalhe"
                            else:
                                final_url = f"https://pje.trt{trt_number}.jus.br/pjekz/processo/{process_id}/detalhe"

                            print(f"final_url: {final_url}")  # Print final_url
                            # Close the id_url tab
                            driver.close()

                            # Switch to the last tab before opening the final_url
                            driver.switch_to.window(driver.window_handles[-1])

                            # Open the final_url in a new tab
                            driver.execute_script(f"window.open('{final_url}', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])
                            # Wait for the page to load (adjust the wait as needed)
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".conteudo-historico")))

                            # Change the gridTemplateColumns style
                            driver.execute_script(
                                "document.querySelector('.conteudo-historico').style.gridTemplateColumns = '1fr 2fr 0%';"
                            )                            
                            continue  # Continue monitoring clipboard content
                    else:
                        continue            
            except Exception as e:
                if "no such window" in str(e).lower():
                    print("[DEBUG] Detected 'no such window' error. Checking if a new tab is needed...")
                    try:
                        if len(driver.window_handles) == 0:
                            driver.execute_script("window.open('about:blank', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])
                        else:
                            print("[DEBUG] Tabs are still available. Switching to the last tab...")
                            driver.switch_to.window(driver.window_handles[-1])
                            print("[DEBUG] Successfully switched to the last tab.")
                    except Exception as tab_error:
                        print(f"[ERROR] Failed to handle 'no such window' scenario: {tab_error}")
            finally:
                time.sleep(1)  # Wait before checking the clipboard again

    except Exception as e:
        print(f"An error occurred in the main loop: {e}")
        update_credentials(driver)

# Function to prompt user for credentials using a GUI and save them to a file
def prompt_for_credentials(file_path, credentials, driver=None):
    main_window = tk.Tk()
    main_window.title("PJE Automático")
    main_window.attributes('-topmost', True)
    main_window.configure(bg=BACKGROUND_COLOR)

    # Set custom icon for the tkinter window
    main_window.iconbitmap(TKINTER_ICON_PATH)

    # Add the logowide.png image to the interface
    logo_image = tk.PhotoImage(file=LOGO_PATH)
    main_window.logo_image = logo_image  # Retain a reference to prevent garbage collection
    logo_label = tk.Label(main_window, image=logo_image, bg=BACKGROUND_COLOR)
    logo_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))

    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    window_width = 500
    window_height = 550
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    main_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 10)
    title_font_style = ("Montserrat", 14, "bold")

    # Add the alert message
    tk.Label(main_window, text="Certifique-se de possuir o Google Chrome instalado!", bg=BACKGROUND_COLOR, fg="red", font=font_style).grid(row=1, column=0, columnspan=2, pady=(5, 10))

    # Login method options
    tk.Label(main_window, text="Método de login:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font_style).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    login_method = tk.StringVar(value="1")  # Default to the first option

    methods = [
        ("1 Somente PJE (login PDPJ CPF e senha)", "1"),
        ("2 Somente PJE (token)", "2"),
        ("3 Astrea + PJE (login PDPJ CPF e Senha)", "3"),
        ("4 Astrea + PJE (Token)", "4"),
        ("5 Somente Astrea", "5")
    ]

    for i, (text, value) in enumerate(methods):
        tk.Radiobutton(main_window, text=text, variable=login_method, value=value, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font_style).grid(row=2 + i, column=1, sticky="w")

    # Add a "Mostrar senhas" checkbox
    def toggle_password_visibility():
        show = "" if show_password_var.get() else "*"
        password_pje_entry.config(show=show)
        password_astrea_entry.config(show=show)

    show_password_var = tk.BooleanVar(value=False)
    show_password_checkbox = tk.Checkbutton(
        main_window, text="Mostrar senhas", variable=show_password_var, command=toggle_password_visibility,
        bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font_style, activebackground=BACKGROUND_COLOR
    )
    show_password_checkbox.grid(row=7, column=0, columnspan=2, pady=10, sticky="n")

    # Input fields
    tk.Label(main_window, text="CPF para login no PDPJ:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font_style).grid(row=8, column=0, padx=10, pady=5, sticky="e")
    username_pje_entry = tk.Entry(main_window, width=40, font=font_style)
    username_pje_entry.grid(row=8, column=1, padx=10, pady=5)
    username_pje_entry.insert(0, credentials.get("USERNAMEPJE", ""))

    tk.Label(main_window, text="Senha para login no PDPJ:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font_style).grid(row=9, column=0, padx=10, pady=5, sticky="e")
    password_pje_entry = tk.Entry(main_window, show='*', width=40, font=font_style)
    password_pje_entry.grid(row=9, column=1, padx=10, pady=5)
    password_pje_entry.insert(0, credentials.get("PASSWORDPJE", ""))

    tk.Label(main_window, text="E-mail do Astrea:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font_style).grid(row=10, column=0, padx=10, pady=5, sticky="e")
    username_astrea_entry = tk.Entry(main_window, width=40, font=font_style)
    username_astrea_entry.grid(row=10, column=1, padx=10, pady=5)
    username_astrea_entry.insert(0, credentials.get("USERNAMEASTREA", ""))

    tk.Label(main_window, text="Senha do Astrea:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=font_style).grid(row=11, column=0, padx=10, pady=5, sticky="e")
    password_astrea_entry = tk.Entry(main_window, show='*', width=40, font=font_style)
    password_astrea_entry.grid(row=11, column=1, padx=10, pady=5)
    password_astrea_entry.insert(0, credentials.get("PASSWORDASTREA", ""))

    # Function to update input field states based on the selected login method
    def update_input_states(*args):
        method = login_method.get()
        if method == "1":  # Somente PJE (login PDPJ CPF e senha)
            username_pje_entry.config(state="normal")
            password_pje_entry.config(state="normal")
            username_astrea_entry.config(state="disabled")
            password_astrea_entry.config(state="disabled")
        elif method == "2":  #2Somente PJE (token)
            username_pje_entry.config(state="disabled")
            password_pje_entry.config(state="disabled")
            username_astrea_entry.config(state="disabled")
            password_astrea_entry.config(state="disabled")
        elif method == "3":  # Astrea + PJE (login PDPJ CPF e Senha)
            username_pje_entry.config(state="normal")
            password_pje_entry.config(state="normal")
            username_astrea_entry.config(state="normal")
            password_astrea_entry.config(state="normal")
        elif method in ["4", "5"]:  # Astrea + PJE (Token) or Somente Astrea
            username_pje_entry.config(state="disabled")
            password_pje_entry.config(state="disabled")
            username_astrea_entry.config(state="normal")
            password_astrea_entry.config(state="normal")

    login_method.trace("w", update_input_states)
    update_input_states()

    def save_and_run():
        username_pje = re.sub(r'\D', '', username_pje_entry.get())
        password_pje = password_pje_entry.get()
        username_astrea = username_astrea_entry.get()
        password_astrea = password_astrea_entry.get()
        selected_login_method = login_method.get()

        # Check required fields based on login method
        required_fields = []
        if selected_login_method in ["1", "3"]:
            if not username_pje or not password_pje:
                messagebox.showerror("Erro", "Preencha o CPF e a senha do PDPJ.")
                return
        if selected_login_method in ["3", "4", "5"]:
            if not username_astrea or not password_astrea:
                messagebox.showerror("Erro", "Preencha o e-mail e a senha do Astrea.")
                return

        credentials = {
            "USERNAMEPJE": username_pje,
            "PASSWORDPJE": password_pje,
            "USERNAMEASTREA": username_astrea,
            "PASSWORDASTREA": password_astrea,
            "LOGIN_METHOD": selected_login_method
        }

        save_credentials(file_path, credentials)

        if driver:
            driver.quit()

        main_window.destroy()
        run_script(credentials)

    tk.Button(main_window, text="Iniciar", command=save_and_run, bg="#ffc477", fg="#333222", width=15, font=font_style).grid(row=12, column=0, columnspan=2, pady=10)

    # Add the current version label at the bottom
    tk.Label(main_window, text=f"Versão: {CURRENT_VERSION}", fg=TEXT_COLOR, bg=BACKGROUND_COLOR, font=("Montserrat", 10)).grid(row=13, column=0, columnspan=2, pady=(5, 10))

    main_window.mainloop()
    return credentials

def prompt_for_pje_level(paste):
    pje_level_window = tk.Tk()
    pje_level_window.title("Escolha o Grau")
    pje_level_window.attributes('-topmost', True)
    pje_level_window.configure(bg="#D9CDFF")

    # Set custom icon for the tkinter window
    pje_level_window.iconbitmap(TKINTER_ICON_PATH)

    screen_width = pje_level_window.winfo_screenwidth()
    screen_height = pje_level_window.winfo_screenheight()
    window_width = 300
    window_height = 300
    position_right = screen_width - window_width - 20  # 20px margin from the right
    position_down = screen_height - window_height - 80  # 50px margin from the bottom
    pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 12)

    tk.Label(pje_level_window, text=f"Detectado o processo\n{paste}", bg="#D9CDFF", fg="#484554", font=(font_style[0], font_style[1], "bold")).pack(pady=10)

    pje_level = tk.StringVar(value="Ignore")  # Default to "Ignore"

    def select_level(level):
        pje_level.set(level)
        pje_level_window.destroy()

    tk.Button(pje_level_window, text="Primeiro Grau PJE", command=lambda: select_level("Primeiro grau PJE"), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Segundo Grau PJE", command=lambda: select_level("Segundo grau PJE"), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="TST PJE", command=lambda: select_level("TST PJE"), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="TST Antigo", command=lambda: select_level("TST Antigo"), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, width=20, font=font_style).pack(pady=5)
    tk.Button(pje_level_window, text="Ignorar e aguardar", command=lambda: select_level("Ignore"), bg=DISABLED_BUTTON_BG_COLOR, fg=TEXT_COLOR, width=20, font=font_style).pack(pady=5)

    # Handle window close event
    def on_close():
        pje_level.set("Ignore")
        pje_level_window.destroy()

    pje_level_window.protocol("WM_DELETE_WINDOW", on_close)

    pje_level_window.mainloop()
    return pje_level.get()

def prompt_reopen_pje(paste):
    """
    Prompt the user with a styled window to decide whether to reopen another PJE level.
    """
    reopen_window = tk.Tk()
    reopen_window.title("Reabrir PJE")
    
    reopen_window.attributes('-topmost', True)
    reopen_window.configure(bg=BACKGROUND_COLOR)

    # Set custom icon for the tkinter window
    reopen_window.iconbitmap(TKINTER_ICON_PATH)

    screen_width = reopen_window.winfo_screenwidth()
    screen_height = reopen_window.winfo_screenheight()
    window_width = 300
    window_height = 350
    position_right = screen_width - window_width - 20 
    position_down = screen_height - window_height - 80  
    reopen_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    font_style = ("Montserrat", 12)
    title_font_style = ("Montserrat", 14, "bold")

    tk.Label(reopen_window, text="Reabrir PJE", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=title_font_style).pack(pady=10)
    tk.Label(
        reopen_window,
        text=(
            f"{paste}\n"
            "\n"
            "Um dos possíveis erros ocorreram:\n"
            " 1) Processo não cadastrado\n"
            " 2) PJE não carregou completamente\n"
            " 3) Número do processo não existe\n"
            "\n"
            "\nDeseja reabrir?"
        ),
        bg=BACKGROUND_COLOR,
        fg=TEXT_COLOR,
        font=font_style,
        wraplength=350,
        justify="center"
    ).pack(pady=10)

    def select_reopen(choice):
        nonlocal reopen_choice
        reopen_choice = choice
        reopen_window.destroy()

    tk.Button(reopen_window, text="Sim", command=lambda: select_reopen(True), bg=BUTTON_BG_COLOR, fg=BUTTON_FG_COLOR, width=15, font=font_style).pack(pady=5)
    tk.Button(reopen_window, text="Não", command=lambda: select_reopen(False), bg=DISABLED_BUTTON_BG_COLOR, fg=TEXT_COLOR, width=15, font=font_style).pack(pady=10)  # Increased bottom padding

    reopen_choice = False
    reopen_window.mainloop()
    return reopen_choice

# Encryption logic
KEY_FILE = os.path.expanduser('~/encryption_key.key')
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(Fernet.generate_key())

# Load the encryption key
with open(KEY_FILE, 'rb') as key_file:
    ENCRYPTION_KEY = key_file.read()

cipher = Fernet(ENCRYPTION_KEY)

def encrypt_credentials(credentials):
    """
    Encrypt the credentials dictionary.
    """
    credentials_json = json.dumps(credentials).encode('utf-8')
    encrypted = cipher.encrypt(credentials_json)
    return encrypted

def decrypt_credentials(encrypted_credentials):
    """
    Decrypt the encrypted credentials.
    """
    decrypted_json = cipher.decrypt(encrypted_credentials).decode('utf-8')
    return json.loads(decrypted_json)

# Save encrypted credentials to a file
def save_credentials(file_path, credentials):
    encrypted = encrypt_credentials(credentials)
    with open(file_path, 'wb') as cred_file:
        cred_file.write(encrypted)

# Load and decrypt credentials from a file
def load_credentials(file_path):
    with open(file_path, 'rb') as cred_file:
        encrypted = cred_file.read()
    return decrypt_credentials(encrypted)

# Load credentials from a file or prompt the user if the file doesn't exist or is invalid
credentials_file = os.path.expanduser('~/credentials.json')
credentials = {}
if os.path.exists(credentials_file):
    try:
        credentials = load_credentials(credentials_file)
    except Exception:
        print("Invalid or corrupted credentials file. Prompting for new credentials...")
        credentials = prompt_for_credentials(credentials_file, credentials)
        save_credentials(credentials_file, credentials)
else:
    credentials = prompt_for_credentials(credentials_file, credentials)
    save_credentials(credentials_file, credentials)

# Allow the user to update credentials
def update_credentials(driver):
    global credentials
    credentials = prompt_for_credentials(credentials_file, credentials, driver)
    save_credentials(credentials_file, credentials)

# Monkey-patch messagebox to make it topmost
def topmost_messagebox(func):
    def wrapper(*args, **kwargs):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()
        result = func(*args, **kwargs)
        root.destroy()
        return result
    return wrapper

messagebox.showinfo = topmost_messagebox(messagebox.showinfo)
messagebox.showwarning = topmost_messagebox(messagebox.showwarning)
messagebox.showerror = topmost_messagebox(messagebox.showerror)
messagebox.askyesno = topmost_messagebox(messagebox.askyesno)

# Show a notification when the program starts
class Notifier:
    def __init__(self, title="PJE Automático", app_icon=ICON_PATH, timeout=5):
        self.title = title
        self.app_icon = app_icon
        self.timeout = timeout
        self.toast_notifier = ToastNotifier()  # Initialize win10toast

    def send(self, message):
        try:
            notification.notify(
                title=self.title,
                message=message,
                app_icon=self.app_icon,
                timeout=self.timeout
            )
        except NotImplementedError:
            print(f"[Notification] {self.title}: {message}")  # Fallback to console output
            try:
                # Use win10toast as a fallback for Windows
                self.toast_notifier.show_toast(self.title, message, icon_path=self.app_icon, duration=self.timeout)
            except Exception as e:
                print(f"[Error] Failed to send notification using win10toast: {e}")

notifier = Notifier()
notifier.send("Para reabrir processos: acesse o ícone da barra de notificações")

prompt_for_credentials(credentials_file, credentials)