"""
Utility functions for the PJE automation system
"""
import re
import time
import tkinter as tk
from tkinter import messagebox
import threading
from config import PROCESS_PATTERNS, SUPPORTED_TRIBUNALS


def identify_tribunal_type(paste):
    """
    Identify the tribunal type based on the process number pattern.
    
    Args:
        paste (str): The process number to analyze
    
    Returns:
        str or None: The tribunal type ('trabalhista', 'tjpe', 'jfpe') or None if not recognized
    """
    # Basic validation - check if it looks like a process number
    if not re.match(r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$', paste):
        return None
    
    # Extract tribunal identifier from process number
    # In Brazilian process numbers: NNNNNNN-DD.AAAA.J.TR.OOOO
    # Where TR is the tribunal identifier
    parts = paste.split('.')
    if len(parts) >= 4:
        tribunal_code = parts[3]
        
        # Trabalhista: codes 01-24 (TRTs) and 90 (TST)
        if tribunal_code in [f"{i:02d}" for i in range(1, 25)] + ['90']:
            return 'trabalhista'
        
        # TJPE: code 05 (assuming Pernambuco state court)
        elif tribunal_code == '05':
            return 'tjpe'
        
        # JFPE: federal courts in Pernambuco region
        elif tribunal_code in ['03', '04']:  # Adjust based on actual codes
            return 'jfpe'
    
    return None


def validate_process_number(process_number):
    """
    Validate if a process number follows the Brazilian standard format.
    
    Args:
        process_number (str): The process number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$', process_number))


def extract_trt_number(process_number):
    """
    Extract TRT number from a trabalhista process number.
    
    Args:
        process_number (str): The process number
    
    Returns:
        str: The TRT number (without leading zeros)
    """
    if len(process_number) >= 20:
        trt_number = process_number[18:20]
        return trt_number.lstrip('0')
    return None


def parse_tst_old_process(process_number):
    """
    Parse TST Antigo process number into its components.
    
    Args:
        process_number (str): The TST process number
    
    Returns:
        dict: Dictionary with process components
    """
    try:
        paste_parts = process_number.split('-')
        numeroTst = paste_parts[0]
        remaining_parts = paste_parts[1].split('.')
        
        return {
            'numeroTst': numeroTst,
            'digitoTst': remaining_parts[0],
            'anoTst': remaining_parts[1],
            'orgaoTst': remaining_parts[2],
            'tribunalTst': remaining_parts[3],
            'varaTst': remaining_parts[4]
        }
    except (IndexError, ValueError):
        return None


def show_notification(message, title="Notificação"):
    """
    Show a notification message to the user.
    
    Args:
        message (str): The message to display
        title (str): The window title
    """
    def show_message():
        messagebox.showinfo(title, message)
    
    # Run in a separate thread to avoid blocking
    threading.Thread(target=show_message, daemon=True).start()


def debounce(wait_time):
    """
    Decorator to debounce function calls.
    
    Args:
        wait_time (float): Time to wait before allowing the next call
    
    Returns:
        function: The decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            wrapper.last_called = getattr(wrapper, 'last_called', 0)
            elapsed = time.time() - wrapper.last_called
            
            if elapsed >= wait_time:
                wrapper.last_called = time.time()
                return func(*args, **kwargs)
            
        return wrapper
    return decorator


def create_centered_window(parent, width, height, title=""):
    """
    Create a centered window relative to the parent.
    
    Args:
        parent: Parent window
        width (int): Window width
        height (int): Window height
        title (str): Window title
    
    Returns:
        tk.Toplevel: The created window
    """
    window = tk.Toplevel(parent)
    window.title(title)
    window.transient(parent)
    window.grab_set()
    
    # Center the window
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
    
    return window


def is_valid_tribunal_type(tribunal_type):
    """
    Check if the tribunal type is supported.
    
    Args:
        tribunal_type (str): The tribunal type to check
    
    Returns:
        bool: True if supported, False otherwise
    """
    return tribunal_type in SUPPORTED_TRIBUNALS


def format_process_number(process_number):
    """
    Format a process number for display.
    
    Args:
        process_number (str): The process number to format
    
    Returns:
        str: The formatted process number
    """
    # Remove any whitespace
    process_number = process_number.strip()
    
    # If it's already properly formatted, return as is
    if validate_process_number(process_number):
        return process_number
    
    # Try to format if it's just digits
    if re.match(r'^\d{20}$', process_number):
        # Format as NNNNNNN-DD.AAAA.J.TR.OOOO
        return f"{process_number[:7]}-{process_number[7:9]}.{process_number[9:13]}.{process_number[13]}.{process_number[14:16]}.{process_number[16:20]}"
    
    return process_number


def safe_get_attribute(element, attribute, default=None):
    """
    Safely get an attribute from a web element.
    
    Args:
        element: Selenium web element
        attribute (str): The attribute name
        default: Default value if attribute doesn't exist
    
    Returns:
        The attribute value or default
    """
    try:
        return element.get_attribute(attribute)
    except:
        return default


def wait_for_condition(condition_func, timeout=10, interval=0.1):
    """
    Wait for a condition to be true.
    
    Args:
        condition_func: Function that returns True when condition is met
        timeout (float): Maximum time to wait
        interval (float): Check interval
    
    Returns:
        bool: True if condition was met, False if timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False
