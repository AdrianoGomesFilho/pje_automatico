import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    subprocess.Popen(["python", script_path])

def on_option_selected(option):
    if option == 1:
        run_script("1astrea_pje_terceiros.py")
    elif option == 2:
        run_script("2astrea_pje_unico.py")
    elif option == 3:
        run_script("3astreaonly.py")
    elif option == 4:
        run_script("44pjeonly_terceiros.py")
    else:
        messagebox.showerror("Erro", "Opção inválida")

root = tk.Tk()
root.title("PJE Automático")

label = tk.Label(root, text="Atualmente a automação é adaptada para acessar processos no PJE trabalhista, de qualquer tribunal. Alguns processos do TST estão disponíveis no PJE.")
label.pack(pady=10)

options = [
    "Opção 1 - Consulta de processos de terceiros + Astrea",
    "Opção 2 - Consulta de processos próprios do token + Astrea",
    "Opção 3 - Consultar processos somente no PJE",
    "Opção 4 - Consultar processos somente no Astrea"
]

for i, option in enumerate(options, start=1):
    button = tk.Button(root, text=option, command=lambda i=i: on_option_selected(i))
    button.pack(fill='x', pady=5)

root.mainloop()