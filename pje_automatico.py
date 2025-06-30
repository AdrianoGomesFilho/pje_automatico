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
from tribunal_handlers import (
    prompt_for_pje_level_trabalhista,
    prompt_for_pje_level_tjpe, 
    prompt_for_pje_level_jfpe,
    handle_trabalhista_login,
    handle_tjpe_login,
    handle_jfpe_login,
    perform_pje_login,
    build_final_url,
    fetch_process_id
)

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
    else:
        print("Browser is already running. Avoiding duplicate instance.")

    # Store the last clipboard content
    last_clipboard_content = ""

    try:
        while True:
            try:
                paste = pyperclip.paste().replace(" ", "").strip()  # Remove all spaces and leading/trailing whitespace

                # Clean the process number by removing any non-numeric characters except hyphens and dots
                import re
                clean_paste = re.sub(r'[^0-9.-]', '', paste)

                # Tribunal type detection by splitting the number and checking the .0.00 part
                tribunal_type = None
                try:
                    # Remove spaces and split by '-' and '.'
                    parts = clean_paste.split('-')
                    if len(parts) == 2:
                        main, rest = parts
                        rest_parts = rest.split('.')
                        if len(rest_parts) == 5:
                            orgao = rest_parts[2]  # the .0.00 part: rest_parts[2] and rest_parts[3]
                            tribunal = rest_parts[3]
                            if orgao == '5':
                                tribunal_type = 'trabalhista'
                            elif orgao == '8' and tribunal == '17':
                                tribunal_type = 'tjpe'
                            elif orgao == '4' and tribunal == '05':
                                tribunal_type = 'jfpe'
                            
                            print(f"[DEBUG] Clean paste: {clean_paste}, Original: {paste}, Tribunal: {tribunal_type}")
                except Exception as e:
                    print(f"[DEBUG] Tribunal detection error: {e}")

                # Check if the clipboard content is new or bypassing is enabled and matches any known pattern
                # Use clean_paste for processing but keep original paste for display
                if bypass_repeated_content or (clean_paste != last_clipboard_content and tribunal_type is not None):
                    print(f"Processo identificado: {clean_paste} (tribunal: {tribunal_type})")
                    add_to_recent(clean_paste)

                    # Ensure we have at least one tab open
                    try:
                        if not driver.window_handles:
                            driver.execute_script("window.open('about:blank', '_blank');")
                        driver.switch_to.window(driver.window_handles[-1])
                    except Exception:
                        # If all else fails, just continue - don't crash
                        print("[INFO] Tab management issue - continuing anyway")
                        continue

                    # Process the new clipboard content
                    last_clipboard_content = clean_paste
                    bypass_repeated_content = False
                    processo_nao_cadastrado = False

                    #########################ASTREA######################################

                    if login_method in ["3", "4", "5"]:  # Only methods that use Astrea
                        try:
                            # Perform Astrea login
                            astrea_url = f"https://app.astrea.net.br/#/main/search-result/{clean_paste}"
                            driver.execute_script(f"window.open('{astrea_url}', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])

                            # Wait for either login form or search element
                            element_present = WebDriverWait(driver, 25).until(
                                EC.any_of(
                                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Digite seu email']")),
                                    EC.presence_of_element_located((By.ID, "search"))
                                )
                            )

                            if element_present.get_attribute("id") != "search":
                                # Login required
                                username_field = driver.find_element(By.NAME, "username")
                                password_field = driver.find_element(By.NAME, "password")
                                username_field.send_keys(usuario_astrea)
                                password_field.send_keys(senha_astrea)
                                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                                login_button.click()
                                print("Astrea login realizado.")
                        except Exception as e:
                            print(f"Astrea error (continuing anyway): {e}")

                    ##################PJE########################################
                    while True:
                        # Prompt user to choose the PJE level based on tribunal type
                        if tribunal_type == 'trabalhista':
                            pje_level = prompt_for_pje_level_trabalhista(clean_paste)
                        elif tribunal_type == 'tjpe':
                            pje_level = prompt_for_pje_level_tjpe(clean_paste)
                        elif tribunal_type == 'jfpe':
                            pje_level = prompt_for_pje_level_jfpe(clean_paste)
                        else:
                            print(f"Tribunal type '{tribunal_type}' not recognized. Skipping...")
                            break

                        if pje_level == "Ignore":
                            print("Opção ignorada. Aguardando novo conteúdo na área de transferência.")
                            break

                        # Handle login based on tribunal type
                        if tribunal_type == 'trabalhista':
                            success, process_id, final_url, should_break, bypass_repeated_content, processo_nao_cadastrado = handle_trabalhista_login(driver, clean_paste, pje_level, usuario_pje, senha_pje, login_method, notifier)
                        elif tribunal_type == 'tjpe':
                            success, process_id, final_url, should_break, bypass_repeated_content, processo_nao_cadastrado = handle_tjpe_login(driver, clean_paste, pje_level, usuario_pje, senha_pje, login_method, notifier)
                        elif tribunal_type == 'jfpe':
                            success, process_id, final_url, should_break, bypass_repeated_content, processo_nao_cadastrado = handle_jfpe_login(driver, clean_paste, pje_level, usuario_pje, senha_pje, login_method, notifier)
                        else:
                            print(f"Unexpected tribunal type '{tribunal_type}' in handler section")
                            break
                        
                        if should_break:
                            break  # For special cases like TST Antigo
                        
                        if not success:
                            break  # Exit the loop and reopen the PJE level prompt
                        else:
                            break  # Exit the loop if process_id is successfully fetched
                    # Handle final URL processing and errors
                    if processo_nao_cadastrado:
                        reopen_choice = prompt_reopen_pje(clean_paste)
                        if reopen_choice:
                            bypass_repeated_content = True
                            continue
                        else:
                            print(f"Opção ignorada para o processo {clean_paste}. Aguardando novo conteúdo na área de transferência.")
                            bypass_repeated_content = False
                            continue
                    
                    # Only process final URL if we have one
                    if final_url is not None:
                        if pje_level == "Ignore":
                            print("Opção ignorada. Aguardando novo conteúdo na área de transferência.")
                            continue
                        
                        print(f"final_url: {final_url}")
                        # Safely close current tab and open final URL
                        try:
                            driver.close()
                        except Exception:
                            pass  # Don't care if close fails
                        
                        try:
                            # Get available windows and switch to last one
                            if driver.window_handles:
                                driver.switch_to.window(driver.window_handles[-1])
                            else:
                                # No windows left, create one
                                driver.execute_script("window.open('about:blank', '_blank');")
                                driver.switch_to.window(driver.window_handles[-1])
                            
                            driver.execute_script(f"window.open('{final_url}', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])
                            
                            # Try to apply styling, but don't crash if it fails
                            try:
                                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".conteudo-historico")))
                                driver.execute_script(
                                    "document.querySelector('.conteudo-historico').style.gridTemplateColumns = '1fr 2fr 0%';"
                                )
                            except Exception:
                                pass  # Don't care if styling fails
                                
                        except Exception as e:
                            print(f"Tab management error (continuing): {e}")
                    
                    continue            
            except Exception as e:
                # Don't crash on any error - just log and continue
                print(f"Error (continuing): {e}")
                try:
                    # Ensure we have at least one window
                    if not driver.window_handles:
                        driver.execute_script("window.open('about:blank', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
                except Exception:
                    # If even this fails, just continue the loop
                    pass
            finally:
                time.sleep(1)

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
    login_method = tk.StringVar(value="")  # No default - user must select

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
        else:  # No method selected - disable all fields
            username_pje_entry.config(state="disabled")
            password_pje_entry.config(state="disabled")
            username_astrea_entry.config(state="disabled")
            password_astrea_entry.config(state="disabled")

    login_method.trace("w", update_input_states)
    update_input_states()

    def save_and_run():
        username_pje = re.sub(r'\D', '', username_pje_entry.get())
        password_pje = password_pje_entry.get()
        username_astrea = username_astrea_entry.get()
        password_astrea = password_astrea_entry.get()
        selected_login_method = login_method.get()

        # Check if login method is selected
        if not selected_login_method:
            messagebox.showerror("Erro", "Por favor, selecione um método de login.")
            return

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