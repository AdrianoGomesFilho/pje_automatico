"""
Tribunal handlers dispatcher - imports and provides access to individual tribunal handlers
"""
from handlers import TrabalhistaHandler, TjpeHandler, Trf5Handler

# Initialize handlers
_trabalhista_handler = TrabalhistaHandler()
_tjpe_handler = TjpeHandler()
_trf5_handler = Trf5Handler()

# Mapping of tribunal types to their handlers
TRIBUNAL_HANDLERS = {
    'trabalhista': _trabalhista_handler,
    'tjpe': _tjpe_handler,
    'trf5': _trf5_handler,
}


def get_handler(tribunal_type):
    """
    Get the handler for a specific tribunal type.
    
    Args:
        tribunal_type (str): The type of tribunal ('trabalhista', 'tjpe', 'trf5')
    
    Returns:
        BaseTribunalHandler: The handler instance for the tribunal
    
    Raises:
        ValueError: If the tribunal type is not supported
    """
    if tribunal_type not in TRIBUNAL_HANDLERS:
        raise ValueError(f"Unsupported tribunal type: {tribunal_type}")
    
    return TRIBUNAL_HANDLERS[tribunal_type]


# Legacy function wrappers for backward compatibility
def prompt_for_pje_level_trabalhista(paste):
    """Legacy wrapper for trabalhista prompt."""
    return _trabalhista_handler.prompt_for_pje_level(paste)


def prompt_for_pje_level_tjpe(paste):
    """Legacy wrapper for TJPE prompt."""
    return _tjpe_handler.prompt_for_pje_level(paste)


def prompt_for_pje_level_trf5(paste):
    """Legacy wrapper for TRF5 prompt."""
    return _trf5_handler.prompt_for_pje_level(paste)


def handle_trabalhista_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
    """Legacy wrapper for trabalhista login."""
    return _trabalhista_handler.handle_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier)


def handle_tjpe_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
    """Legacy wrapper for TJPE login."""
    return _tjpe_handler.handle_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier)


def handle_trf5_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier):
    """Legacy wrapper for TRF5 login."""
    return _trf5_handler.handle_login(driver, paste, pje_level, usuario_pje, senha_pje, login_method, notifier)


# Additional legacy wrappers for backward compatibility
def perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method):
    """Legacy wrapper for PJE login - uses the base handler's method."""
    from handlers.base_handler import BaseTribunalHandler
    base_handler = BaseTribunalHandler("Legacy")
    return base_handler.perform_pje_login(driver, base_url, usuario_pje, senha_pje, login_method)


def fetch_process_id(driver, id_url):
    """Legacy wrapper for process ID fetching - uses the base handler's method."""
    from handlers.base_handler import BaseTribunalHandler
    base_handler = BaseTribunalHandler("Legacy")
    return base_handler.fetch_process_id(driver, id_url)


def build_final_url(tribunal_type, pje_level, process_id, paste):
    """
    Legacy wrapper for building final URL based on tribunal type and PJE level.
    """
    if tribunal_type == 'trabalhista':
        trt_number = paste[18:20].lstrip('0')
        if pje_level == "TST PJE":
            return f"https://pje.tst.jus.br/pjekz/processo/{process_id}/detalhe"
        else:
            return f"https://pje.trt{trt_number}.jus.br/pjekz/processo/{process_id}/detalhe"
    
    elif tribunal_type == 'tjpe':
        return f"https://pje.tjpe.jus.br/pjekz/processo/{process_id}/detalhe"
    
    elif tribunal_type == 'trf5':
        if pje_level == "Juizado":
            return f"https://pje.jfpe.jus.br/pjekz/processo/{process_id}/detalhe"
        elif pje_level == "Justiça comum":
            return f"https://pje.trf5.jus.br/pjekz/processo/{process_id}/detalhe"
    
    return None
