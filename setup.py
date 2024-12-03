
import subprocess
import os

# Install required packages
subprocess.check_call(["pip", "install", "-r", "requirements.txt"])

# Create a shortcut to run the main script
shortcut_content = """
[InternetShortcut]
URL=file:///c:/Users/fish/script_pje/main.py
IconIndex=0
IconFile=python.exe
"""
with open("PJE_Automatico.url", "w") as shortcut_file:
    shortcut_file.write(shortcut_content)

print("Setup complete. Use the 'PJE_Automatico.url' shortcut to run the application.")