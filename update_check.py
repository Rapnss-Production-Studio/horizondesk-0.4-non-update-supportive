import sys
import os
import time
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox

# Configuration
VERSION_URL = 'https://horizon-online.api-rapnss.workers.dev/versions.json'
CURRENT_VERSION = '0.2'
UPDATER_SCRIPT = 'updater.py'
MAIN_GUI_SCRIPT = os.path.join('sample-gui', 'main_gui.py')

def get_latest_version_info():
    """Fetches the latest version info from the server."""
    try:
        response = requests.get(VERSION_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[UpdateCheck] Failed to fetch version info: {e}")
        return None

def launch_updater():
    """Launches updater.py and exits this script."""
    print("[UpdateCheck] Launching updater.py...")
    try:
        if sys.platform == 'win32':
            # Create process independent of the current one
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen([sys.executable, UPDATER_SCRIPT], creationflags=DETACHED_PROCESS)
        else:
            subprocess.Popen([sys.executable, UPDATER_SCRIPT], start_new_session=True)
    except Exception as e:
        print(f"[UpdateCheck] Failed to launch updater: {e}")
    sys.exit(0)

def launch_main_gui():
    """Launches main_gui.py and exits this script."""
    print("[UpdateCheck] Launching main_gui.py...")
    try:
        # We need to change cwd to sample-gui because main_gui.py expects to run from there
        cwd = os.path.dirname(os.path.abspath(MAIN_GUI_SCRIPT))
        if sys.platform == 'win32':
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen([sys.executable, os.path.basename(MAIN_GUI_SCRIPT)], cwd=cwd, creationflags=DETACHED_PROCESS)
        else:
            subprocess.Popen([sys.executable, os.path.basename(MAIN_GUI_SCRIPT)], cwd=cwd, start_new_session=True)
    except Exception as e:
        print(f"[UpdateCheck] Failed to launch main_gui: {e}")
    sys.exit(0)

def center_window(root):
    """Centers the tkinter window on the screen."""
    root.eval('tk::PlaceWindow . center')

def main():
    print(f"[UpdateCheck] Checking for updates (Current version: {CURRENT_VERSION})...")
    
    info = get_latest_version_info()
    
    if info and 'latest' in info:
        latest_version = info['latest']
        print(f"[UpdateCheck] Latest version reported by server: {latest_version}")
        
        # Simple string comparison is fine for basic semver like 0.2 vs 0.3
        # In the future, a proper semver library could be used.
        try:
            current_parts = [int(x) for x in CURRENT_VERSION.split('.')]
            latest_parts = [int(x) for x in latest_version.split('.')]
            
            is_newer = False
            for c, l in zip(current_parts, latest_parts):
                if l > c:
                    is_newer = True
                    break
                elif l < c:
                    break
                    
            if len(latest_parts) > len(current_parts) and not is_newer:
                is_newer = True # e.g. 0.2 vs 0.2.1
                
        except ValueError:
            # Fallback to simple string logic if parsing fails
            is_newer = latest_version != CURRENT_VERSION
            
        if is_newer:
            print("[UpdateCheck] Update available! Prompting user...")
            
            # Hide the main tkinter window, we only want the messagebox
            root = tk.Tk()
            root.withdraw()
            
            release_notes = info.get('release_notes', 'A new update is available!')
            msg = f"A new version ({latest_version}) of Horizon Desk is available.\n\nRelease Notes:\n{release_notes}\n\nWould you like to install it now?"
            
            # Ask yes/no
            response = messagebox.askyesno("Update Available", msg, parent=root)
            root.destroy()
            
            if response:
                launch_updater()
            else:
                print("[UpdateCheck] User declined update.")
                launch_main_gui()
        else:
            print("[UpdateCheck] You are up to date.")
            launch_main_gui()
    else:
        print("[UpdateCheck] Could not determine latest version. Launching app normally.")
        launch_main_gui()

if __name__ == "__main__":
    main()
