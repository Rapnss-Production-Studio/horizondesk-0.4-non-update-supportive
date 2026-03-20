
import os
import json
import ctypes
import shutil
import statistics
from pathlib import Path
from PIL import Image
import winreg
import icon_manager

# Constants
WALLPAPER_KEY = winreg.HKEY_CURRENT_USER
WALLPAPER_SUBKEY = "Control Panel\\Desktop"
WALLPAPER_VALUE = "WallPaper"

BACKUP_DIR = Path.home() / "AppData" / "Local" / "HorizonDesk" / "backups"
CONFIG_FILE = Path.home() / "AppData" / "Local" / "HorizonDesk" / "config.json"

class ThemeManager:
    """Manages wallpapers, colors, and backups"""
    
    def __init__(self):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.initialize()
        
    def initialize(self):
        """Perform initial backup if needed"""
        if not (BACKUP_DIR / "default.json").exists():
            self.backup_current_state("default")
            
    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                pass
        return {}
        
    def _save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.config, indent=2))

    def get_current_wallpaper(self):
        """Get path to current Windows wallpaper"""
        try:
            with winreg.OpenKey(WALLPAPER_KEY, WALLPAPER_SUBKEY) as key:
                path, _ = winreg.QueryValueEx(key, WALLPAPER_VALUE)
                if os.path.exists(path):
                    return path
        except:
            pass
        
        try:
            ubuf = ctypes.create_unicode_buffer(512)
            ctypes.windll.user32.SystemParametersInfoW(0x0073, 512, ubuf, 0)
            return ubuf.value
        except:
            return None

    def backup_current_state(self, backup_name="default"):
        """Backup current wallpaper"""
        wallpaper = self.get_current_wallpaper()
        backup_data = {
            "wallpaper": wallpaper,
            "timestamp": str(os.path.getmtime(wallpaper) if wallpaper and os.path.exists(wallpaper) else 0)
        }
        backup_file = BACKUP_DIR / f"{backup_name}.json"
        backup_file.write_text(json.dumps(backup_data, indent=2))
        print(f"✓ Backup saved to {backup_file}")
        
    def restore_state(self, backup_name="default"):
        """Restore wallpaper and default icons"""
        backup_file = BACKUP_DIR / f"{backup_name}.json"
        if not backup_file.exists():
            return False
            
        try:
            data = json.loads(backup_file.read_text())
            wallpaper = data.get("wallpaper")
            
            if wallpaper and os.path.exists(wallpaper):
                self.set_wallpaper(wallpaper)
            
            # Restore default icons
            icon_manager.restore_default_icons()
            
            # Reset config
            if 'theme' in self.config:
                del self.config['theme']
                self._save_config()
                
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def set_wallpaper(self, path):
        """Set desktop background"""
        path = str(Path(path).absolute())
        if not os.path.exists(path):
            return False
        try:
            ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, path, 0x01 | 0x02)
            return True
        except:
            return False

    def extract_accent_color(self, image_path):
        """Extract dominant color from image"""
        try:
            img = Image.open(image_path)
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            
            w, h = img.size
            center = img.crop((w//4, h//4, 3*w//4, 3*h//4))
            
            pixels = list(center.getdata())
            r_total, g_total, b_total = 0, 0, 0
            count = 0
            
            for p in pixels:
                if len(p) > 3 and p[3] < 128: continue
                r_total += p[0]
                g_total += p[1]
                b_total += p[2]
                count += 1
                
            if count > 0:
                return (r_total//count, g_total//count, b_total//count)
            return (139, 92, 246)
        except:
            return (139, 92, 246)

    def apply_theme(self, wallpaper_path):
        """Apply theme: Wallpaper + Icons + Config"""
        print(f"Applying theme: {wallpaper_path}")
        
        self.set_wallpaper(wallpaper_path)
        accent = self.extract_accent_color(wallpaper_path)
        
        # Save to config
        self.config['theme'] = {
            'accent': f'#{accent[0]:02x}{accent[1]:02x}{accent[2]:02x}',
            'wallpaper': str(wallpaper_path)
        }
        self._save_config()
        
        # Update icons
        icon_manager.generate_themed_icons(accent)
        icon_manager.apply_to_all_desktop_folders()
        
        return accent

    def get_current_theme(self):
        """Get current theme config"""
        return self.config.get('theme')

    def get_theme_palette(self, mode='light'):
        """Get color palette with user overrides"""
        overrides = self.config.get('theme', {}).get('custom_colors', {})
        base_accent = self.config.get('theme', {}).get('accent', '#6366f1')
        
        # Default Light Palette
        palette = {
            'mode': 'light',
            'bg_glass': '#ffffff',
            'bg_glass_light': '#f9fafb',
            'bg_glass_card': '#ffffff',
            'bg_hover': '#f3f4f6',
            'bg_active': '#e5e7eb',
            'text': '#111827',
            'text_secondary': '#4b5563',
            'text_muted': '#9ca3af',
            'accent': base_accent,
            'accent_light': '#818cf8',
            'accent_glow': base_accent,
            'border': '#e5e7eb',
            'border_glow': '#c7d2fe',
            'success': '#059669',
            'warning': '#d97706',
            'info': '#3b82f6',
            'user_bubble': '#eff6ff',
            'ai_bubble': '#f3f4f6',
            'input_bg': '#f9fafb'
        }
        
        # Apply overrides
        palette.update(overrides)
        return palette

    def get_font(self, size=10, weight=None):
        """Get font tuple based on user settings"""
        family = self.config.get('theme', {}).get('font_family', 'Segoe UI Variable Display')
        base_weight = self.config.get('theme', {}).get('font_weight', 'light') # Users requested thin/light
        
        # Map weight names to Tkinter weights/styles if needed, 
        # but Tkinter font tuple is (family, size, style)
        # Style can be 'bold', 'italic', 'roman', 'bold italic'
        # Regular/Light usually just means omitting 'bold'.
        
        style = weight if weight else ""
        if base_weight == 'bold' and 'bold' not in style:
            style = 'bold'
        elif base_weight == 'light':
             # Tkinter doesn't strictly support 'light' as a style keyword usually, 
             # it depends on the installed font family name (e.g. "Segoe UI Light").
             # If the user selected a font that supports it, great. 
             # If they selected "Segoe UI" and want light, we might need "Segoe UI Light".
             if 'Segoe UI' in family and 'Light' not in family:
                 family = 'Segoe UI Light'
        
        return (family, size, style)

    def get_window_style(self):
        """Get selected window control style"""
        return self.config.get('theme', {}).get('window_style', 'macos')

    def save_custom_color(self, key, value):
        """Save a specific color override"""
        if 'theme' not in self.config: self.config['theme'] = {}
        if 'custom_colors' not in self.config['theme']: self.config['theme']['custom_colors'] = {}
        self.config['theme']['custom_colors'][key] = value
        self._save_config()

    def save_font_settings(self, family, weight):
        if 'theme' not in self.config: self.config['theme'] = {}
        self.config['theme']['font_family'] = family
        self.config['theme']['font_weight'] = weight
        self._save_config()

    def save_window_style(self, style):
        if 'theme' not in self.config: self.config['theme'] = {}
        self.config['theme']['window_style'] = style
        self._save_config()
        
if __name__ == "__main__":
    tm = ThemeManager()
    print("Theme Manager initialized.")
