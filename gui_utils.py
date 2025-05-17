import tkinter as tk
from tkinter import messagebox

# GUI color/style constants (can be imported from main if needed)
BACKGROUND_COLOR = "#ECE9FD"
TEXT_COLOR = "#3F3D56"
BUTTON_BG_COLOR = "#A084E8"
BUTTON_FG_COLOR = "#FFFFFF"
DISABLED_BUTTON_BG_COLOR = "#CFCBE7"
LOGO_PATH = None  # Set by main if needed
TKINTER_ICON_PATH = None  # Set by main if needed
CURRENT_VERSION = None  # Set by main if needed


def show_update_alert(latest_version, site_url, icon_path):
    alert_window = tk.Tk()
    alert_window.title("Atualização Disponível")
    alert_window.attributes('-topmost', True)
    alert_window.configure(bg="#ECE9FD")
    alert_window.iconbitmap(icon_path)
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
    def open_site():
        import webbrowser
        webbrowser.open(site_url)
        alert_window.destroy()
        import sys
        sys.exit(0)
    tk.Button(alert_window, text="Ir para download", command=open_site, bg="#A084E8", fg="#FFFFFF", font=font_style, width=25).pack(pady=5)
    def close_window():
        alert_window.destroy()
    tk.Button(alert_window, text="Continuar com a versão atual", command=close_window, bg="#CFCBE7", fg="#3F3D56", font=font_style, width=25).pack(pady=5)
    def close_program():
        alert_window.destroy()
        import sys
        sys.exit(0)
    alert_window.protocol("WM_DELETE_WINDOW", close_program)
    tk.Button(alert_window, text="Fechar", command=close_program, bg="#CFCBE7", fg="#3F3D56", font=font_style, width=20).pack(pady=5)
    alert_window.mainloop()


def prompt_for_credentials(file_path, credentials, save_credentials_func, run_script_func, icon_path, logo_path, current_version, bg_color, text_color, button_bg, button_fg, disabled_button_bg):
    # This is a simplified version. You can move your full implementation here.
    # ...existing code...
    pass


def prompt_for_pje_level(paste, icon_path, button_bg, button_fg, disabled_button_bg, text_color):
    # ...existing code...
    pass


def prompt_reopen_pje(paste, icon_path, bg_color, text_color, button_bg, button_fg, disabled_button_bg):
    # ...existing code...
    pass


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
