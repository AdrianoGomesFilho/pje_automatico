"""
Template for creating new tribunal handlers
Copy this file and modify it for new tribunals.
"""
import tkinter as tk
from selenium.common.exceptions import TimeoutException

from .base_handler import BaseTribunalHandler


class TemplateHandler(BaseTribunalHandler):
    """
    Template handler for new tribunals.
    Replace 'Template' with your tribunal name (e.g., TjspHandler, TrfHandler, etc.)
    """
    
    def __init__(self):
        # Update the tribunal name
        super().__init__("TEMPLATE")  # Change to your tribunal name
    
    def prompt_for_pje_level(self, paste):
        """
        Prompt user to choose PJE level for this tribunal's processes.
        Customize the options based on your tribunal's structure.
        """
        pje_level_window, font_style = self.create_prompt_window("Escolha o Grau - TEMPLATE", paste, 250)
        
        pje_level = tk.StringVar(value="Ignore")

        def select_level(level):
            pje_level.set(level)
            pje_level_window.destroy()

        # Add tribunal-specific buttons - customize these based on your tribunal
        self.add_button(pje_level_window, "Primeira Instância", lambda: select_level("Primeira Instância"), font_style)
        self.add_button(pje_level_window, "Segunda Instância", lambda: select_level("Segunda Instância"), font_style)
        # Add more buttons as needed:
        # self.add_button(pje_level_window, "Tribunal Superior", lambda: select_level("Tribunal Superior"), font_style)
        
        # Add ignore button
        self.add_ignore_button(pje_level_window, pje_level, font_style)

        pje_level_window.mainloop()
        return pje_level.get()
    
    def handle_login(self, driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
        """
        Handle complete login process for this tribunal including process ID fetching.
        Returns: (success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
        
        Customize the URLs and logic based on your tribunal's specific requirements.
        """
        # Define URLs based on PJE level - customize these
        if pje_level == "Primeira Instância":
            base_url = "https://pje.template.jus.br/1g/login.seam"  # Update URL
            id_url = f"https://pje.template.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"  # Update URL
        elif pje_level == "Segunda Instância":
            base_url = "https://pje.template.jus.br/2g/login.seam"  # Update URL
            id_url = f"https://pje.template.jus.br/pje-consulta-api/api/processos/dadosbasicos/{paste}"  # Update URL
        # Add more elif blocks for additional levels
        else:
            # Unknown PJE level
            return False, None, None, False, True, True
        
        # Perform login using the base handler's method
        success = self.perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method)
        
        if not success:
            return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado
        
        try:
            # Fetch process ID using the base handler's method
            process_id = self.fetch_process_id(driver, id_url)
            
            # Build final URL - customize based on your tribunal's URL structure
            final_url = f"https://pje.template.jus.br/pjekz/processo/{process_id}/detalhe"  # Update URL
            
            return True, process_id, final_url, False, False, False  # success
        except (ValueError, TimeoutException):
            return False, None, None, False, True, True  # failed, enable bypass, processo_nao_cadastrado


# Steps to add a new tribunal:
# 1. Copy this file to handler_[tribunal_name].py
# 2. Replace "Template" with your tribunal name (e.g., "Tjsp", "Trf3", etc.)
# 3. Update the tribunal name in __init__
# 4. Customize the prompt_for_pje_level method with your tribunal's options
# 5. Update URLs in handle_login method
# 6. Add tribunal identification logic to utils.py identify_tribunal_type function
# 7. Add your handler to handlers/__init__.py
# 8. Add your handler to tribunal_handlers.py TRIBUNAL_HANDLERS dict
# 9. Update config.py with your tribunal's URL templates if needed
# 10. Test your new handler
