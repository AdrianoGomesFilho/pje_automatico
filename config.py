"""
Configuration constants for the PJE automation system
"""
import os
import sys

# Icon path setup
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(__file__)

ICON_PATH = os.path.join(BASE_PATH, "icon.ico")

# UI Configuration
WINDOW_CONFIG = {
    'bg_color': "#D9CDFF",
    'text_color': "#484554",
    'button_color': "#A084E8",
    'button_text_color': "#FFFFFF",
    'ignore_button_color': "#CFCBE7",
    'ignore_button_text_color': "#3F3D56",
    'font_family': "Montserrat",
    'font_size': 12,
    'window_width': 300,
    'window_offset_right': 20,
    'window_offset_bottom': 80,
}

# Process patterns for tribunal identification
PROCESS_PATTERNS = {
    'trabalhista': r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$',
    'tjpe': r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$',  # Add specific TJPE pattern if different
    'jfpe': r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$',  # Add specific JFPE pattern if different
}

# URL Templates
URL_TEMPLATES = {
    'trabalhista': {
        'first_degree': "https://pje.trt{trt_number}.jus.br/primeirograu/login.seam",
        'second_degree': "https://pje.trt{trt_number}.jus.br/segundograu/login.seam",
        'tst': "https://pje.tst.jus.br/tst/login.seam",
        'tst_old': "https://consultaprocessual.tst.jus.br/consultaProcessual/consultaTstNumUnica.do",
        'api': "https://pje.trt{trt_number}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{process}",
        'tst_api': "https://pje.tst.jus.br/pje-consulta-api/api/processos/dadosbasicos/{process}",
    },
    'tjpe': {
        'first_degree': "https://pje.tjpe.jus.br/1g/login.seam",
        'second_degree': "https://pje.tjpe.jus.br/2g/login.seam",
        'api': "https://pje.tjpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{process}",
        'detail': "https://pje.tjpe.jus.br/pjekz/processo/{process_id}/detalhe",
    },
    'jfpe': {
        'juizado': "https://pje.jfpe.jus.br/pje/login.seam",
        'common': "https://pje.trf5.jus.br/pje/login.seam",
        'juizado_api': "https://pje.jfpe.jus.br/pje-consulta-api/api/processos/dadosbasicos/{process}",
        'common_api': "https://pje.trf5.jus.br/pje-consulta-api/api/processos/dadosbasicos/{process}",
        'juizado_detail': "https://pje.jfpe.jus.br/pjekz/processo/{process_id}/detalhe",
        'common_detail': "https://pje.trf5.jus.br/pjekz/processo/{process_id}/detalhe",
    }
}

# Timeouts (in seconds)
TIMEOUTS = {
    'page_load': 10,
    'login': 30,
    'api_call': 10,
}

# Supported tribunal types
SUPPORTED_TRIBUNALS = ['trabalhista', 'tjpe', 'jfpe']
