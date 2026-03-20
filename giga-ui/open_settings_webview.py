"""
Horizon Settings Webview — Opens settings React app with JS bridge
Usage: python open_settings_webview.py <html_path>
Reads/writes config from LOCALAPPDATA/HorizonDesk/config.json
"""
import sys
import os
import json
import threading
import ctypes

HORIZON_DIR = os.path.join(os.environ.get('LOCALAPPDATA', '.'), 'HorizonDesk')
CONFIG_FILE = os.path.join(HORIZON_DIR, 'config.json')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_config(cfg):
    os.makedirs(HORIZON_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)


class SettingsAPI:
    """JS bridge for the HTML settings app — runs in subprocess"""

    def get_config(self):
        return load_config().get('theme_tweaks', {})

    def set_color(self, key, value):
        cfg = load_config()
        cfg.setdefault('theme_tweaks', {})[key] = value
        save_config(cfg)

    def set_slider(self, key, value):
        cfg = load_config()
        cfg.setdefault('theme_tweaks', {})[key] = int(value)
        save_config(cfg)
        # Live wallpaper opacity
        if key == 'taskbar_opacity':
            pass  # Applied on next launcher restart

    def apply_font(self, font_name):
        cfg = load_config()
        cfg.setdefault('theme_tweaks', {})['font_family'] = font_name
        save_config(cfg)

    def reset_layout(self):
        cfg = load_config()
        tw = cfg.get('theme_tweaks', {})
        for k in ('taskbar_height', 'prompt_width', 'prompt_height', 'prompt_offset'):
            tw.pop(k, None)
        cfg['theme_tweaks'] = tw
        save_config(cfg)

    def browse_wallpaper(self):
        """Open file dialog and set wallpaper"""
        def do_browse():
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                path = filedialog.askopenfilename(
                    title="Select Wallpaper",
                    filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
                )
                root.destroy()
                if path:
                    ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, path, 0x01 | 0x02)
            except Exception as ex:
                print(f"  ⚠ Browse error: {ex}")
        threading.Thread(target=do_browse, daemon=True).start()

    def restore_wallpaper(self):
        pass

    def generate_icon_preview(self, template, color):
        def do_gen():
            try:
                sys.path.insert(0, SCRIPT_DIR)
                import icon_manager
                hex_c = color.lstrip('#')
                rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
                icon_manager.create_icon_from_template(template, rgb)
            except Exception as ex:
                print(f'  ⚠ Icon preview: {ex}')
        threading.Thread(target=do_gen, daemon=True).start()

    def apply_icon_template(self, template, color):
        def do_apply():
            try:
                sys.path.insert(0, SCRIPT_DIR)
                import icon_manager
                hex_c = color.lstrip('#')
                rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
                ico_path = icon_manager.create_icon_from_template(template, rgb)
                from pathlib import Path
                desktop = Path.home() / 'Desktop'
                for folder in desktop.iterdir():
                    if folder.is_dir() and not folder.name.startswith('.'):
                        icon_manager.apply_folder_icon(folder, ico_path)
                ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
                print("  ✓ Icons applied")
            except Exception as ex:
                print(f'  ⚠ Icon apply: {ex}')
        threading.Thread(target=do_apply, daemon=True).start()

    def restore_default_icons(self):
        def do_restore():
            try:
                sys.path.insert(0, SCRIPT_DIR)
                import icon_manager
                icon_manager.restore_default_icons()
                print("  ✓ Default icons restored")
            except Exception as ex:
                print(f'  ⚠ Restore: {ex}')
        threading.Thread(target=do_restore, daemon=True).start()

    def close_settings(self):
        """Close the settings window"""
        if hasattr(self, '_window') and self._window:
            self._window.destroy()


def main():
    if len(sys.argv) < 2:
        print("Usage: python open_settings_webview.py <html_path>")
        sys.exit(1)

    html_path = sys.argv[1]
    if not os.path.exists(html_path):
        print(f"Settings not found: {html_path}")
        sys.exit(1)

    import webview
    api = SettingsAPI()
    window = webview.create_window(
        'Horizon Settings',
        url=html_path,
        js_api=api,
        width=700,
        height=540,
        resizable=True,
        min_size=(550, 420)
    )
    api._window = window
    webview.start()


if __name__ == '__main__':
    main()
