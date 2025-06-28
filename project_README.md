# PJE Automático - Modular Architecture

This document describes the improved modular architecture of the PJE automation system.

## Project Structure

```
pje_automatico/
├── pje_automatico.py          # Main application script
├── tribunal_handlers.py       # Tribunal handler dispatcher
├── config.py                 # Configuration constants
├── utils.py                  # Utility functions
├── handlers/                 # Tribunal-specific handlers
│   ├── __init__.py          # Package initialization
│   ├── base_handler.py      # Base handler class
│   ├── handler_trabalhista.py  # TRT/TST handler
│   ├── handler_tjpe.py      # TJPE handler
│   ├── handler_jfpe.py      # JFPE handler
│   ├── handler_template.py  # Template for new handlers
│   └── README.md           # Handler documentation
├── icon.ico                 # Application icon
├── logowide.png            # Application logo
└── README.md               # This file
```

## Architecture Overview

The system has been refactored into a modular architecture that makes it easy to add support for new tribunals:

### 1. Main Application (`pje_automatico.py`)
- Handles clipboard monitoring
- Manages WebDriver
- Coordinates with tribunal handlers
- Handles Astrea integration
- Manages application lifecycle

### 2. Tribunal Handler Dispatcher (`tribunal_handlers.py`)
- Provides centralized access to all tribunal handlers
- Maintains backward compatibility with legacy function calls
- Acts as a registry for supported tribunals

### 3. Individual Tribunal Handlers (`handlers/`)
- Each tribunal has its own dedicated handler file
- Inherits common functionality from `BaseTribunalHandler`
- Implements tribunal-specific prompt and login logic
- Easy to maintain and extend

### 4. Configuration (`config.py`)
- Centralized configuration constants
- UI styling parameters
- URL templates for tribunals
- Timeout settings

### 5. Utilities (`utils.py`)
- Process number validation and parsing
- Tribunal type identification
- Common helper functions
- Notification utilities

## Currently Supported Tribunals

| Tribunal | Handler | Supported Levels |
|----------|---------|------------------|
| **Trabalhista (TRT/TST)** | `TrabalhistaHandler` | Primeiro Grau PJE, Segundo Grau PJE, TST PJE, TST Antigo |
| **TJPE** | `TjpeHandler` | Primeiro grau TJPE, Segundo grau TJPE |
| **JFPE** | `JfpeHandler` | Juizado, Justiça comum |

## Adding a New Tribunal

To add support for a new tribunal (e.g., TJSP):

### Step 1: Create the Handler
Copy `handlers/handler_template.py` to `handlers/handler_tjsp.py` and customize:

```python
class TjspHandler(BaseTribunalHandler):
    def __init__(self):
        super().__init__("TJSP")
    
    def prompt_for_pje_level(self, paste):
        # Implement TJSP-specific prompt
        pass
    
    def handle_login(self, driver, paste, pje_level, ...):
        # Implement TJSP-specific login logic
        pass
```

### Step 2: Update Package Initialization
Add to `handlers/__init__.py`:

```python
from .handler_tjsp import TjspHandler
__all__ = ['TrabalhistaHandler', 'TjpeHandler', 'JfpeHandler', 'TjspHandler']
```

### Step 3: Register the Handler
Add to `tribunal_handlers.py`:

```python
from handlers import TjspHandler

_tjsp_handler = TjspHandler()

TRIBUNAL_HANDLERS = {
    'trabalhista': _trabalhista_handler,
    'tjpe': _tjpe_handler,
    'jfpe': _jfpe_handler,
    'tjsp': _tjsp_handler,  # Add this line
}
```

### Step 4: Update Tribunal Detection
Add detection logic to `utils.py` `identify_tribunal_type()` function:

```python
def identify_tribunal_type(paste):
    # ... existing logic ...
    elif tribunal_code == '26':  # Example: TJSP code
        return 'tjsp'
```

### Step 5: Test
Test with real TJSP process numbers to ensure everything works correctly.

## Benefits of the Modular Architecture

### 1. **Maintainability**
- Each tribunal's logic is isolated in its own file
- Changes to one tribunal don't affect others
- Easier to debug and test individual tribunals

### 2. **Scalability**
- Adding new tribunals is straightforward
- Common functionality is shared through the base handler
- Consistent patterns across all handlers

### 3. **Code Reusability**
- Base handler provides common UI and login patterns
- Shared utilities for process validation and parsing
- Consistent error handling across tribunals

### 4. **Flexibility**
- Each handler can customize its behavior as needed
- Special cases (like TST Antigo) are handled gracefully
- Easy to update URLs or logic for specific tribunals

## Code Organization Best Practices

### Handler Implementation
- Always inherit from `BaseTribunalHandler`
- Use the base handler's utility methods when possible
- Handle exceptions gracefully and return appropriate error states
- Document any special requirements or behaviors

### URL Management
- Use the URL templates in `config.py` when possible
- Keep URLs up to date as tribunal systems change
- Test all URL patterns with real process numbers

### Error Handling
- Return consistent error states from handlers
- Log errors for debugging purposes
- Provide meaningful error messages to users

### Testing
- Test with real process numbers from each tribunal
- Verify all PJE levels work correctly
- Test both successful and error scenarios

## Migration Notes

The refactoring maintains backward compatibility:
- Existing function names in `tribunal_handlers.py` still work
- Main application logic remains largely unchanged
- All existing functionality is preserved

## Future Enhancements

Potential improvements to consider:

1. **Configuration File Support**: Load tribunal configurations from external files
2. **Plugin System**: Allow dynamic loading of tribunal handlers
3. **Enhanced Error Reporting**: Better error tracking and reporting
4. **Automated Testing**: Unit tests for each tribunal handler
5. **Web Interface**: Alternative to the desktop application

## Conclusion

The modular architecture makes the PJE automation system much more maintainable and extensible. Adding support for new tribunals is now a straightforward process that doesn't require deep knowledge of the entire codebase.
