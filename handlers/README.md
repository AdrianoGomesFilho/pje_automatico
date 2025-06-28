# Tribunal Handlers

This directory contains modular handlers for different Brazilian tribunal systems in the PJE automation project.

## Structure

- `__init__.py` - Package initialization and handler exports
- `base_handler.py` - Base class with common functionality for all tribunal handlers
- `handler_trabalhista.py` - Handler for Trabalhista (TRT/TST) processes
- `handler_tjpe.py` - Handler for TJPE (Tribunal de Justiça de Pernambuco) processes
- `handler_jfpe.py` - Handler for JFPE (Justiça Federal de Pernambuco) processes
- `handler_template.py` - Template for creating new tribunal handlers

## How It Works

Each tribunal handler inherits from `BaseTribunalHandler` and implements:

1. **`prompt_for_pje_level(paste)`** - Shows a UI dialog for users to select the appropriate PJE level/instance for the process
2. **`handle_login(driver, paste, pje_level, ...)`** - Handles the complete login process and returns processing results

The base handler provides common functionality like:
- UI window creation and styling
- PJE login procedures
- Process ID fetching from APIs
- Common utility methods

## Adding a New Tribunal

To add support for a new tribunal:

1. **Copy the template**: Use `handler_template.py` as your starting point
2. **Customize the handler**: 
   - Update class name and tribunal name
   - Modify PJE level options in `prompt_for_pje_level`
   - Update URLs and logic in `handle_login`
3. **Update tribunal identification**: Add detection logic to `utils.py`
4. **Register the handler**: Add it to `__init__.py` and `tribunal_handlers.py`
5. **Test thoroughly**: Ensure all PJE levels work correctly

## Example: Adding TJSP Support

```python
# handlers/handler_tjsp.py
from .base_handler import BaseTribunalHandler

class TjspHandler(BaseTribunalHandler):
    def __init__(self):
        super().__init__("TJSP")
    
    def prompt_for_pje_level(self, paste):
        # Create prompt with TJSP-specific options
        # e.g., "Primeira Instância", "Segunda Instância"
        pass
    
    def handle_login(self, driver, paste, pje_level, ...):
        # Handle TJSP login with appropriate URLs
        # e.g., https://pje.tjsp.jus.br/...
        pass
```

Then register it:

```python
# handlers/__init__.py
from .handler_tjsp import TjspHandler
__all__ = [..., 'TjspHandler']

# tribunal_handlers.py
_tjsp_handler = TjspHandler()
TRIBUNAL_HANDLERS = {
    ...,
    'tjsp': _tjsp_handler,
}
```

## Handler Methods Return Values

The `handle_login` method should return a tuple:
```python
(success, process_id, final_url, should_continue, bypass_repeated_content, processo_nao_cadastrado)
```

Where:
- `success` (bool) - Whether the login was successful
- `process_id` (str/None) - The fetched process ID from the API
- `final_url` (str/None) - The final URL to open for the process
- `should_continue` (bool) - Whether to break from the main loop (e.g., for TST Antigo)
- `bypass_repeated_content` (bool) - Whether to enable content bypass
- `processo_nao_cadastrado` (bool) - Whether the process wasn't found

## Common Patterns

### Standard PJE Login
Most tribunals follow the standard PJE login pattern:
1. Open login page
2. Click PDPJ button
3. Handle authentication (certificate or username/password)
4. Fetch process ID from API
5. Build final process URL

### Special Cases
Some tribunals have special handling:
- **TST Antigo**: Opens old TST consultation system instead of PJE
- **Multi-instance tribunals**: Different URLs for different instances
- **Federal vs State**: Different URL patterns and structures

## Best Practices

1. **Use the base handler methods** when possible to maintain consistency
2. **Handle exceptions gracefully** and return appropriate error states
3. **Test with real process numbers** from your tribunal
4. **Keep URLs up to date** as tribunal systems change
5. **Document any special requirements** in your handler's docstring

## Troubleshooting

Common issues when adding new tribunals:

1. **Tribunal not detected**: Check `utils.py` identification logic
2. **Login fails**: Verify URLs and authentication flow
3. **Process ID not found**: Check API URL format and response structure
4. **Final URL incorrect**: Verify the detail page URL pattern

For debugging, enable debug prints in your handler and test with known process numbers.
