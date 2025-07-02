"""
Test script to verify power management functionality
"""
import time
import threading
import win32api
import win32con
import win32gui
import ctypes
from ctypes import wintypes

class TestPowerManager:
    def __init__(self):
        self.is_suspended = False
        self.suspend_count = 0
        self.resume_count = 0
        self._setup_power_management()
    
    def _setup_power_management(self):
        """Setup Windows power management event handling"""
        try:
            # Create a hidden window to receive power management messages
            self.hwnd = self._create_hidden_window()
            if self.hwnd:
                print("[TestPowerManager] Power management initialized successfully")
                return True
            else:
                print("[TestPowerManager] Failed to create hidden window")
                return False
        except Exception as e:
            print(f"[TestPowerManager] Setup error: {e}")
            return False
    
    def _create_hidden_window(self):
        """Create a hidden window to receive Windows messages"""
        try:
            # Define window class
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._window_proc
            wc.lpszClassName = "TestPJE_PowerManager"
            wc.hInstance = win32api.GetModuleHandle(None)
            
            # Register window class
            class_atom = win32gui.RegisterClass(wc)
            
            # Create hidden window
            hwnd = win32gui.CreateWindow(
                class_atom, "Test PJE Power Manager",
                0, 0, 0, 0, 0, 0, 0,
                win32api.GetModuleHandle(None), None
            )
            
            return hwnd
        except Exception as e:
            print(f"[TestPowerManager] Window creation error: {e}")
            return None
    
    def _window_proc(self, hwnd, msg, wparam, lparam):
        """Window procedure to handle power management messages"""
        if msg == win32con.WM_POWERBROADCAST:
            if wparam == win32con.PBT_APMQUERYSUSPEND:
                print("[TestPowerManager] System is preparing to suspend")
                self._on_suspend()
                return True  # Allow suspend
            elif wparam == win32con.PBT_APMRESUMESUSPEND:
                print("[TestPowerManager] System resumed from suspend")
                self._on_resume()
            elif wparam == win32con.PBT_APMSUSPEND:
                print("[TestPowerManager] System is suspending")
                self._on_suspend()
        
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    def _on_suspend(self):
        """Handle system suspend event"""
        self.is_suspended = True
        self.suspend_count += 1
        print(f"[TestPowerManager] Handling suspend event #{self.suspend_count}")
    
    def _on_resume(self):
        """Handle system resume event"""
        self.is_suspended = False
        self.resume_count += 1
        print(f"[TestPowerManager] Handling resume event #{self.resume_count}")
    
    def start_message_loop(self):
        """Start the Windows message loop in a separate thread"""
        def message_loop():
            try:
                print("[TestPowerManager] Starting message loop...")
                while True:
                    msg = win32gui.GetMessage(None, 0, 0)
                    if msg == (-1, 0, 0, 0):  # Error occurred
                        break
                    win32gui.TranslateMessage(msg)
                    win32gui.DispatchMessage(msg)
            except Exception as e:
                print(f"[TestPowerManager] Message loop error: {e}")
        
        message_thread = threading.Thread(target=message_loop, daemon=True)
        message_thread.start()
        return message_thread

def main():
    print("Testing Power Management System...")
    print("This script will monitor for system suspend/resume events.")
    print("Try putting your computer to sleep to test the functionality.")
    print("Press Ctrl+C to exit.\n")
    
    # Initialize power manager
    power_manager = TestPowerManager()
    
    # Start message loop
    message_thread = power_manager.start_message_loop()
    
    try:
        # Monitor loop
        while True:
            status = "SUSPENDED" if power_manager.is_suspended else "ACTIVE"
            print(f"[Monitor] Status: {status} | Suspends: {power_manager.suspend_count} | Resumes: {power_manager.resume_count}")
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n[Monitor] Exiting...")
    except Exception as e:
        print(f"[Monitor] Error in main loop: {e}")

if __name__ == "__main__":
    main()
