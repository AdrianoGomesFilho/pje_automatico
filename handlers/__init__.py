"""
Handlers package for tribunal-specific logic

This __init__.py file serves three main purposes:
1. Makes the 'handlers' directory a Python package
2. Defines the public API by importing all handler classes
3. Controls what gets exported when using 'from handlers import *'
"""

# Import all handler classes to make them available at package level
# This allows: from handlers import TrabalhistaHandler
# Instead of: from handlers.handler_trabalhista import TrabalhistaHandler
from .handler_trabalhista import TrabalhistaHandler
from .handler_tjpe import TjpeHandler
from .handler_trf5 import Trf5Handler

# Define what gets exported with 'from handlers import *'
# This is the "public API" of the handlers package
__all__ = ['TrabalhistaHandler', 'TjpeHandler', 'Trf5Handler']

# When you import the package, these classes are immediately available:
# from handlers import TrabalhistaHandler  ✅ Works
# from handlers import SomeInternalFunction  ❌ Not in __all__, so not exported
