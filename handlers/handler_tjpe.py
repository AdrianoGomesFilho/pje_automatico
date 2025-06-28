"""
TJPE (Tribunal de Justiça de Pernambuco) tribunal handler
"""
import tkinter as tk
from selenium.common.exceptions import TimeoutException

from .base_handler import BaseTribunalHandler


class TjpeHandler(BaseTribunalHandler):
    """
    Handler for TJPE (Tribunal de Justiça de Pernambuco) processes.
    """
    
    def __init__(self):
        super().__init__("TJPE")
    
    def prompt_for_pje_level(self, paste):
        """
        Prompt user to choose PJE level for TJPE processes.
        """
        pje_level_window, font_style = self.create_prompt_window("Escolha o Grau - TJPE", paste, 250)
        
        pje_level = tk.StringVar(value="Ignore")

        def select_level(level):
            pje_level.set(level)
            pje_level_window.destroy()

        # Add tribunal-specific buttons
        self.add_button(pje_level_window, "Primeiro grau TJPE", lambda: select_level("Primeiro grau TJPE"), font_style)
        self.add_button(pje_level_window, "Segundo grau TJPE", lambda: select_level("Segundo grau TJPE"), font_style)
        
        # Add ignore button
        self.add_ignore_button(pje_level_window, pje_level, font_style)

        pje_level_window.mainloop()
        return pje_level.get()
    
    def handle_login(self, driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
        """
        Handle complete TJPE login process including process ID fetching.
        Returns: (success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
        """
        if pje_level == "Primeiro grau TJPE":
            base_url = "https://pje.tjpe.jus.br/1g/login.seam"
            id_url = f"https://pje.tjpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
        elif pje_level == "Segundo grau TJPE":
            base_url = "https://pje.tjpe.jus.br/2g/login.seam"
            id_url = f"https://pje.tjpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"
        
        # Perform login and fetch process ID
        success = self.perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method)
        
        if not success:
            return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
        
        try:
            process_id = self.fetch_process_id(driver, id_url)
            final_url = f"https://pje.tjpe.jus.br/pjekz/processo/{process_id}/detalhe"
            return True, process_id, final_url, False, False, False  # success
        except (ValueError, TimeoutException):
            return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
