"""
Horizon Giga UI - Windows System Modifier
Actually modifies Windows taskbar, icons, and desktop
"""

import ctypes
import os
import sys
import json
import winreg
import subprocess
from ctypes import wintypes

# Windows API Constants
SW_HIDE = 0
SW_SHOW = 5
GW_CHILD = 5

# Load Windows DLLs
user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# Config file path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'giga_config.json')

class WindowsUIModifier:
    """Modify Windows UI elements"""
    
    def __init__(self):
        self.taskbar_hidden = False
        self.original_taskbar_pos = None
        self.load_config()
    
    def load_config(self):
        """Load saved configuration"""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'mode': 'windows',  # 'windows' or 'giga'
                'taskbar_hidden': False,
                'dock_position': 'bottom',
                'dock_size': 56
            }
    
    def save_config(self):
        """Save configuration"""
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # ==================== TASKBAR CONTROL ====================
    
    def get_taskbar_handle(self):
        """Get Windows taskbar window handle"""
        return user32.FindWindowW("Shell_TrayWnd", None)
    
    def hide_taskbar(self):
        """Hide the Windows taskbar"""
        hwnd = self.get_taskbar_handle()
        if hwnd:
            user32.ShowWindow(hwnd, SW_HIDE)
            self.taskbar_hidden = True
            self.config['taskbar_hidden'] = True
            self.save_config()
            print("✓ Windows taskbar hidden")
            return True
        return False
    
    def show_taskbar(self):
        """Show the Windows taskbar"""
        hwnd = self.get_taskbar_handle()
        if hwnd:
            user32.ShowWindow(hwnd, SW_SHOW)
            self.taskbar_hidden = False
            self.config['taskbar_hidden'] = False
            self.save_config()
            print("✓ Windows taskbar restored")
            return True
        return False
    
    def toggle_taskbar(self):
        """Toggle taskbar visibility"""
        if self.taskbar_hidden:
            return self.show_taskbar()
        else:
            return self.hide_taskbar()
    
    # ==================== TASKBAR AUTO-HIDE ====================
    
    def set_taskbar_autohide(self, enable=True):
        """Enable/disable taskbar auto-hide via registry"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                                winreg.KEY_READ | winreg.KEY_WRITE)
            
            settings = bytearray(winreg.QueryValueEx(key, "Settings")[0])
            
            # Byte 8 controls auto-hide: 0x03 = auto-hide, 0x02 = always show
            if enable:
                settings[8] = 0x03
            else:
                settings[8] = 0x02
            
            winreg.SetValueEx(key, "Settings", 0, winreg.REG_BINARY, bytes(settings))
            winreg.CloseKey(key)
            
            # Restart Explorer to apply changes
            self._restart_explorer()
            
            print(f"✓ Taskbar auto-hide {'enabled' if enable else 'disabled'}")
            return True
        except Exception as e:
            print(f"✗ Failed to set taskbar auto-hide: {e}")
            return False
    
    def _restart_explorer(self):
        """Restart Windows Explorer to apply changes"""
        os.system("taskkill /f /im explorer.exe")
        subprocess.Popen("explorer.exe")
        print("✓ Explorer restarted")
    
    # ==================== DESKTOP ICONS ====================
    
    def hide_desktop_icons(self):
        """Hide all desktop icons"""
        # Find the desktop window
        progman = user32.FindWindowW("Progman", None)
        
        # Send message to toggle icons
        user32.SendMessageW(progman, 0x052C, 0, 0)
        print("✓ Desktop icons toggled")
    
    def get_desktop_path(self):
        """Get user's desktop path"""
        return os.path.join(os.path.expanduser("~"), "Desktop")
    
    # ==================== FOLDER ICON CHANGER ====================
    
    def change_folder_icon(self, folder_path, icon_path):
        """Change a folder's icon to custom icon"""
        desktop_ini = os.path.join(folder_path, "desktop.ini")
        
        # Create desktop.ini content
        content = f"""[.ShellClassInfo]
IconResource={icon_path},0
"""
        
        try:
            # Set folder as system folder
            os.system(f'attrib +s "{folder_path}"')
            
            # Write desktop.ini
            with open(desktop_ini, 'w') as f:
                f.write(content)
            
            # Set desktop.ini as hidden system file
            os.system(f'attrib +h +s "{desktop_ini}"')
            
            # Refresh folder
            shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
            
            print(f"✓ Changed icon for: {folder_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to change icon: {e}")
            return False
    
    def restore_folder_icon(self, folder_path):
        """Restore folder to default icon"""
        desktop_ini = os.path.join(folder_path, "desktop.ini")
        
        try:
            if os.path.exists(desktop_ini):
                os.system(f'attrib -h -s "{desktop_ini}"')
                os.remove(desktop_ini)
            
            os.system(f'attrib -s "{folder_path}"')
            shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
            
            print(f"✓ Restored default icon for: {folder_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to restore icon: {e}")
            return False
    
    # ==================== SCREEN INFO ====================
    
    def get_screen_size(self):
        """Get primary screen resolution"""
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return width, height
    
    def get_taskbar_height(self):
        """Get Windows taskbar height"""
        hwnd = self.get_taskbar_handle()
        if hwnd:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            return rect.bottom - rect.top
        return 40  # Default
    
    # ==================== GIGA MODE ====================
    
    def enable_giga_mode(self):
        """Enable Horizon Giga UI mode"""
        print("\n🚀 Enabling Horizon Giga UI...")
        
        # Hide Windows taskbar
        self.hide_taskbar()
        
        # Update config
        self.config['mode'] = 'giga'
        self.save_config()
        
        print("\n✓ Giga UI Mode enabled!")
        print("  - Windows taskbar: Hidden")
        print("  - Run 'giga_dock.py' to start the dock")
        return True
    
    def disable_giga_mode(self):
        """Disable Giga UI and restore Windows mode"""
        print("\n🔄 Restoring Windows UI...")
        
        # Show Windows taskbar
        self.show_taskbar()
        
        # Update config
        self.config['mode'] = 'windows'
        self.save_config()
        
        print("\n✓ Windows Mode restored!")
        return True
    
    def get_current_mode(self):
        """Get current UI mode"""
        return self.config.get('mode', 'windows')


# ==================== CLI Interface ====================

def main():
    modifier = WindowsUIModifier()
    
    print("\n╔══════════════════════════════════════════╗")
    print("║     Horizon Giga UI - Windows Modifier    ║")
    print("╚══════════════════════════════════════════╝")
    
    print(f"\nCurrent Mode: {modifier.get_current_mode().upper()}")
    print(f"Screen Size: {modifier.get_screen_size()}")
    
    print("\nCommands:")
    print("  1. Enable Giga UI Mode")
    print("  2. Restore Windows Mode")
    print("  3. Toggle Taskbar")
    print("  4. Set Taskbar Auto-hide")
    print("  5. Hide Desktop Icons")
    print("  6. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                modifier.enable_giga_mode()
            elif choice == '2':
                modifier.disable_giga_mode()
            elif choice == '3':
                modifier.toggle_taskbar()
            elif choice == '4':
                enable = input("Enable auto-hide? (y/n): ").lower() == 'y'
                modifier.set_taskbar_autohide(enable)
            elif choice == '5':
                modifier.hide_desktop_icons()
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid option")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == '__main__':
    main()
