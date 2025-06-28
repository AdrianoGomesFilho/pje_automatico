"""
Handlers package for tribunal-specific logic
"""

from .handler_trabalhista import TrabalhistaHandler
from .handler_tjpe import TjpeHandler
from .handler_jfpe import JfpeHandler

__all__ = ['TrabalhistaHandler', 'TjpeHandler', 'JfpeHandler']
