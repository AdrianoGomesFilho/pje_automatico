"""
JFPE (Justiça Federal de Pernambuco) tribunal handler
"""
import tkinter as tk
from selenium.common.exceptions import TimeoutException

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
        pje_level_window, font_style = self.create_prompt_window("Escolha o Grau - JFPE", paste, 250)
        
        pje_level = tk.StringVar(value="Ignore")

        def select_level(level):
            pje_level.set(level)
            pje_level_window.destroy()

        # Add tribunal-specific buttons
        self.add_button(pje_level_window, "Juizado", lambda: select_level("Juizado"), font_style)
        self.add_button(pje_level_window, "Justiça comum", lambda: select_level("Justiça comum"), font_style)
        
        # Add ignore button
        self.add_ignore_button(pje_level_window, pje_level, font_style)

        pje_level_window.mainloop()
        return pje_level.get()
    
    def handle_login(self, driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
        """
        Handle complete JFPE login process including process ID fetching.
        Returns: (success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
        """
        if pje_level == "Juizado":
            base_url = "https://pje.jfpe.jus.br/pje/login.seam"
            id_url = f"https://pje.jfpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
        elif pje_level == "Justiça comum":
            base_url = "https://pje.trf5.jus.br/pje/login.seam"
            id_url = f"https://pje.trf5.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
        
        # Perform login and fetch process ID
        success = self.perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method)
        
        if not success:
            return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
        
        try:
            process_id = self.fetch_process_id(driver, id_url)
            if pje_level == "Juizado":
                final_url = f"https://pje.jfpe.jus.br/pjekz/processo/{process_id}/detalhe"
            else:  # Justiça comum
                final_url = f"https://pje.trf5.jus.br/pjekz/processo/{process_id}/detalhe"
            return True, process_id, final_url, False, False, False  # success
        except (ValueError, TimeoutException):
            return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
