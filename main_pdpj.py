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


# Function to prompt user for credentials using a GUI and save them to a file
def prompt_for_credentials(file_path, credentials, driver=None):
    main_window = tk.Tk()
    main_window.title("PJE automático")
    main_window.attributes('-topmost', True)  # Make the window stay on top

    # Get the screen width and height
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    # Calculate the position to center the window
    window_width = 500  # Increased width
    window_height = 260
    position_right = int(screen_width/2 - window_width/2)
    position_down = int(screen_height/2 - window_height/2)

    # Set the geometry of the window
    main_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    tk.Label(main_window, text="E-mail do Astrea:").grid(row=2, column=0, padx=10, pady=5)
    username_astrea_entry = tk.Entry(main_window, width=40)  # Increased width
    username_astrea_entry.grid(row=2, column=1, padx=10, pady=5)
    username_astrea_entry.insert(0, credentials.get("USERNAMEASTREA", ""))

    tk.Label(main_window, text="Senha do Astrea:").grid(row=3, column=0, padx=10, pady=5)
    password_astrea_entry = tk.Entry(main_window, show='*', width=40)  # Increased width
    password_astrea_entry.grid(row=3, column=1, padx=10, pady=5)
    password_astrea_entry.insert(0, credentials.get("PASSWORDASTREA", ""))

    tk.Label(main_window, text="CPF para login no PJE:").grid(row=0, column=0, padx=10, pady=5)
    username_pje_entry = tk.Entry(main_window, width=40)  # Increased width
    username_pje_entry.grid(row=0, column=1, padx=10, pady=5)
    username_pje_entry.insert(0, credentials.get("USERNAMEPJE", ""))

    tk.Label(main_window, text="Senha para login no PJE:").grid(row=1, column=0, padx=10, pady=5)
    password_pje_entry = tk.Entry(main_window, show='*', width=40)  # Increased width
    password_pje_entry.grid(row=1, column=1, padx=10, pady=5)
    password_pje_entry.insert(0, credentials.get("PASSWORDPJE", ""))

    tk.Label(main_window, text="Método de Login:").grid(row=4, column=0, padx=10, pady=5)
    login_method = tk.StringVar()
    login_method_combobox = ttk.Combobox(main_window, textvariable=login_method, state='readonly', width=37)  # Increased width
    login_method_combobox['values'] = (
        "Astrea + PJE (Senha)",  
        "Astrea + PJE (Token)",  
        "Somente Astrea",  
        "Somente PJE"
    )
    login_method_combobox.grid(row=4, column=1, padx=10, pady=5)
    login_method_combobox.current(0)  # Set default value

    def save_and_run(event=None):
        username_pje = re.sub(r'\D', '', username_pje_entry.get())  # Remove all non-numeric characters
        password_pje = password_pje_entry.get()
        username_astrea = username_astrea_entry.get()
        password_astrea = password_astrea_entry.get()
        selected_login_method = login_method.get()

        if not username_pje or not password_pje or not username_astrea or not password_astrea:
            messagebox.showerror("Erro", "Precisar preencher todos os campos!")
            return

        credentials = {
            "USERNAMEPJE": username_pje,
            "PASSWORDPJE": password_pje,
            "USERNAMEASTREA": username_astrea,
            "PASSWORDASTREA": password_astrea,
            "LOGIN_METHOD": selected_login_method
        }

        with open(file_path, 'w') as cred_file:
            json.dump(credentials, cred_file)

        if driver:
            driver.quit()

        main_window.destroy()
        run_script(credentials)


    tk.Button(main_window, text="Iniciar", command=save_and_run).grid(row=5, column=0, columnspan=2, pady=10)

    main_window.bind('<Return>', save_and_run)

    main_window.mainloop()
    return credentials

def prompt_for_pje_level():
    pje_level_window = tk.Tk()
    pje_level_window.title("Deseja abrir o processo")
    pje_level_window.attributes('-topmost', True)

    screen_width = pje_level_window.winfo_screenwidth()
    screen_height = pje_level_window.winfo_screenheight()
    window_width = 400  # Increased width
    window_height = 150
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    pje_level_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    tk.Label(pje_level_window, text="Escolha o grau:").pack(pady=10)
    pje_level = tk.StringVar()
    pje_level_combobox = ttk.Combobox(pje_level_window, textvariable=pje_level, state='readonly', width=37)  # Increased width
    pje_level_combobox['values'] = ("Primeiro grau", "Segundo grau", "TST")
    pje_level_combobox.pack(pady=10)
    pje_level_combobox.current(0)
    pje_level_combobox.bind('<Return>', lambda e: on_select())

    def on_select(event=None):
        pje_level_window.destroy()

    ok_button = tk.Button(pje_level_window, text="OK", command=on_select)
    ok_button.pack(pady=10)
    pje_level_window.bind('<Return>', on_select)
    ok_button.bind('<Return>', on_select)

    pje_level_window.mainloop()
    return pje_level.get()

# Load credentials from a file or prompt the user if the file doesn't exist
credentials_file = os.path.expanduser('~/credentials.json')
credentials = {}
if os.path.exists(credentials_file):
    with open(credentials_file, 'r') as cred_file:
        credentials = json.load(cred_file)
else:
    credentials = prompt_for_credentials(credentials_file, credentials)

# Allow the user to update credentials
def update_credentials(driver):
    global credentials
    credentials = prompt_for_credentials(credentials_file, credentials, driver)

# Function to run the main script
def run_script(credentials):
    global usuario_pje, senha_pje, usuario_astrea, senha_astrea, login_method, pje_level
    usuario_pje = credentials["USERNAMEPJE"]
    senha_pje = credentials["PASSWORDPJE"]
    usuario_astrea = credentials["USERNAMEASTREA"]
    senha_astrea = credentials["PASSWORDASTREA"]
    login_method = credentials["LOGIN_METHOD"]

    print(f"CPF para login no PJE: {usuario_pje}")
    print(f"Senha para login no PJE: xxxxxxxxxxxx")
    print(f"E-mail do Astrea: {usuario_astrea}")
    print(f"Senha do Astrea: xxxxxxxxxxxx")
    print(f"Método de Login: {login_method}")

    # Specify the path to your Chrome user data directory
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)  # Prevents browser from closing
    chrome_options.add_argument("--start-maximized")  # Open browser in fullscreen

    # Initialize WebDriver with Chrome options
    driver = webdriver.Chrome(options=chrome_options)

    # Store the last clipboard content
    last_clipboard_content = ""

    def find_or_open_tab(driver, base_url, data_url=None):
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if (base_url in driver.current_url or (data_url and data_url in driver.current_url)):
                return handle
        # Switch to the last tab before opening a new one
        driver.switch_to.window(driver.window_handles[-1])
        driver.execute_script(f"window.open('{base_url}', '_blank');")
        new_handle = driver.window_handles[-1]
        return new_handle


    def fetch_process_id(driver, id_url):
        driver.execute_script(f"window.open('{id_url}', '_blank');")
        id_url_handle = driver.window_handles[-1]
        driver.switch_to.window(id_url_handle)
        try:
            # Wait for the page to load and fetch the process ID from the HTML
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            process_id = soup.find('pre').text.strip()
            process_id = json.loads(process_id)[0]['id']
            return process_id
        finally:
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])

    try:
        while True:
            try:
                # Monitor clipboard for specific data pattern
                pattern = re.compile(r'\d{7}-\d{2}\.\d{4}\.5\.\d{2}\.\d{4}')
                paste = pyperclip.paste()

                # Check if the clipboard content is new and matches the pattern
                if paste != last_clipboard_content and pattern.match(paste):
                    print(f"Processo identificado: {paste}")
                    last_clipboard_content = paste  # Update the last clipboard content

                    #########################ASTREA######################################

                    if login_method in ["Astrea + PJE (Senha)", "Astrea", "Astrea + PJE (Token)"]:
                        # Perform Astrea login and other actions
                        astrea_url = f"https://app.astrea.net.br/#/main/search-result/{paste}"
                        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab
                        driver.execute_script(f"window.open('{astrea_url}', '_blank');")
                        astrea_handle = driver.window_handles[-1]
                        driver.switch_to.window(astrea_handle)

                        try:
                            # Check if the login element is present
                            login_element = WebDriverWait(driver, 25).until(
                                EC.presence_of_element_located((By.NAME, "username"))
                            )

                            # Credentials
                            username_field = driver.find_element(By.NAME, "username")
                            password_field = driver.find_element(By.NAME, "password")

                            username_field.send_keys(usuario_astrea)
                            password_field.send_keys(senha_astrea)

                            # Submit the login form
                            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                            login_button.click()

                            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "au-header-app__logo")))
                        except TimeoutException:
                            print("Erro no login.")
                    else:
                        print("Skipping login as already logged in.")
                        
                    # Extract the TRT number (15th and 16th characters)
                    trt_number = paste[18:20]
                    trt_number = trt_number.lstrip('0')

                    # Prompt user to choose the PJE level
                    pje_level = prompt_for_pje_level()

                    if pje_level == "Primeiro grau":
                        base_url = f"https://pje.trt{trt_number}.jus.br/primeirograu/login.seam"
                        id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                    elif pje_level == "Segundo grau":
                        base_url = f"https://pje.trt{trt_number}.jus.br/segundograu/login.seam"
                        id_url = f"https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                    elif pje_level == "TST":
                        base_url = "https://pje.tst.jus.br/tst/login.seam"
                        id_url = f"https://pje.tst.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
                    else:
                        messagebox.showinfo("Aviso", "Esse processo não está cadastrado neste grau")
                        continue  # Skip to the next iteration of the loop

                    base_url_handle = find_or_open_tab(driver, base_url)
                    driver.switch_to.window(base_url_handle)

                    botao_pdpj = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnSsoPdpj")))
                    botao_pdpj.click()
                    
                    elemento_login = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "username")) or
                            EC.presence_of_element_located((By.ID, "brasao-republica"))
                            )

                    if "username" in elemento_login.get_attribute("class"):
                        process_id = fetch_process_id(driver, id_url)
                    else:
                        if login_method == "Astrea + PJE (Token)" or login_method == "PJE (token)":
                            botao_pdpj = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "botao-certificado-titulo")))
                            botao_pdpj.click()
                            elemento_login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "brasao-republica")))
                            process_id = fetch_process_id(driver, id_url)
                        else:
                            driver.find_element(By.ID, "username").send_keys(usuario_pje)
                            driver.find_element(By.ID, "password").send_keys(senha_pje)
                            driver.find_element(By.ID, "kc-login").click()
                            elemento_login = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "brasao-republica")))
                            process_id = fetch_process_id(driver, id_url)
                    
                    # Construct the final_url using the fetched id
                    if pje_level == "TST":
                        final_url = f"https://pje.tst.jus.br/pjekz/processo/{process_id}/detalhe"
                    else:
                        final_url = f"https://pje.trt{trt_number}.jus.br/pjekz/processo/{process_id}/detalhe"

                    print(f"final_url: {final_url}")  # Print final_url

                    # Close the id_url tab
                    driver.close()

                    # Switch to the last tab before opening the final_url
                    driver.switch_to.window(driver.window_handles[-1])

                    # Open the final_url in a new tab
                    final_url_handle = find_or_open_tab(driver, final_url)
                    driver.switch_to.window(final_url_handle)

                    try:
                        # Wait for the element with class 'cabecalho-centro' to be present
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cabecalho-centro")))
                    except TimeoutException:
                        messagebox.showinfo("Aviso", "Processo não cadastrado neste PJE.")
                        driver.close()
                
                    if pje_level == "TST":
                        paste_parts = paste.split('-')
                        numeroTst = paste_parts[0]
                        remaining_parts = paste_parts[1].split('.')
                        digitoTst = remaining_parts[0]
                        anoTst = remaining_parts[1]
                        orgaoTst = remaining_parts[2]
                        tribunalTst = remaining_parts[3]
                        varaTst = remaining_parts[4]

                        antigo_tst_url = f"https://consultaprocessual.tst.jus.br/consultaProcessual/consultaTstNumUnica.do?conscsjt=&numeroTst={numeroTst}&digitoTst={digitoTst}&anoTst={anoTst}&orgaoTst={orgaoTst}&tribunalTst={tribunalTst}&varaTst={varaTst}&consulta=Consultar"

                        print(f"antigo_tst_url: {antigo_tst_url}")  # Print antigo_tst_url

                        messagebox.showinfo("Aviso", "Processo sem cadastro no PJE TST, abrindo o sistema do TST antigo em outra aba...")
                        driver.execute_script(f"window.open('{antigo_tst_url}', '_blank');")

            finally:
                time.sleep(1)  # Wait before checking the clipboard again

    except Exception as e:
        print(f"An error occurred: {e}")
        update_credentials(driver)

# Show the credentials window before running the script
prompt_for_credentials(credentials_file, credentials)