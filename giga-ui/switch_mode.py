"""
Horizon Giga UI - Mode Switcher
Quick toggle between Windows and Giga UI modes
Run this from desktop shortcut
"""

import os
import sys
import json
import ctypes
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / 'giga_config.json'

user32 = ctypes.windll.user32

def load_config():
    """Load config"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {'mode': 'windows'}

def save_config(config):
    """Save config"""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def show_taskbar():
    """Show Windows taskbar"""
    taskbar = user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar:
        user32.ShowWindow(taskbar, 5)  # SW_SHOW
        return True
    return False

def hide_taskbar():
    """Hide Windows taskbar"""
    taskbar = user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar:
        user32.ShowWindow(taskbar, 0)  # SW_HIDE
        return True
    return False

def switch_mode():
    """Toggle between Windows and Giga UI mode"""
    config = load_config()
    current_mode = config.get('mode', 'windows')
    
    if current_mode == 'windows':
        # Switch to Giga
        new_mode = 'giga'
        hide_taskbar()
        config['mode'] = 'giga'
        config['taskbar_hidden'] = True
        save_config(config)
        
        # Start dock
        import subprocess
        subprocess.Popen([sys.executable, str(SCRIPT_DIR / 'giga_dock.py')], 
                        creationflags=subprocess.CREATE_NO_WINDOW)
        
        show_notification("Horizon Giga UI", "Switched to Giga Mode! Dock starting...")
    else:
        # Switch to Windows
        new_mode = 'windows'
        show_taskbar()
        config['mode'] = 'windows'
        config['taskbar_hidden'] = False
        save_config(config)
        
        # Kill dock if running (by finding its window)
        # The dock will close itself when mode switches
        
        show_notification("Horizon Desk", "Switched to Windows Mode! Taskbar restored.")
    
    print(f"Switched from {current_mode} to {new_mode}")

def show_notification(title, message):
    """Show Windows notification"""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=3, threaded=True)
    except:
        # Fallback to message box
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)

def main():
    """Main entry point"""
    switch_mode()

if __name__ == '__main__':
    main()
