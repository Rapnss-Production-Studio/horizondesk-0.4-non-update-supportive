"""
Horizon Desktop Theme — True Desktop Elements
Uses Tkinter overrideredirect (like old giga_dock.py) to create
panels that are PART of the desktop, not separate windows.

Panels:
  1. Taskbar — thin glass strip at top
  2. Prompt — floating rounded pill at bottom center
  3. Settings — overlay panel toggled from taskbar

These are desktop ELEMENTS, not windows:
  ✓ No window frame / chrome
  ✓ No taskbar icon
  ✓ No Alt+Tab entry
  ✓ Not draggable
  ✓ Desktop icons + other windows work normally
"""

import tkinter as tk
from tkinter import font as tkfont
import ctypes
import ctypes.wintypes
import os
import sys
import time
import json
import queue
import threading
import subprocess
import atexit

try:
    import win32gui
    import win32con
    import win32process
    import psutil
except ImportError:
    win32gui = win32con = win32process = psutil = None

try:
    import webview
except ImportError:
    webview = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
APPS_DIR = os.path.join(SCRIPT_DIR, 'apps')
BACKEND_PORT = 15900

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# ─── Config ──────────────────────────────────────────
HORIZON_DIR = os.path.join(os.environ.get('LOCALAPPDATA', '.'), 'HorizonDesk')
CONFIG_FILE = os.path.join(HORIZON_DIR, 'config.json')

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


# ─── Color Palette ───────────────────────────────────
class Colors:
    # Dark glassmorphism palette
    BG_GLASS = '#0E0E1A'
    BG_GLASS_LIGHT = '#161628'
    BG_CARD = '#1A1A2E'
    ACCENT = '#818CF8'
    ACCENT_LIGHT = '#A5B4FC'
    ACCENT_DIM = '#4F46E5'
    TEXT = '#E8E8F0'
    TEXT_MUTED = '#7A7A9A'
    TEXT_DIM = '#4A4A6A'
    BORDER = '#2A2A40'
    BORDER_GLOW = '#343452'
    PROMPT_BG = '#12122A'
    SEND_BG = '#6366F1'
    CLOSE_RED = '#FF5F56'
    TRANSPARENT = '#000000'  # Transparent color key


# ─── Horizon Apps Registry ───────────────────────────
HORIZON_APPS = [
    {'id': 'presentation-studio', 'name': 'Presentation Studio', 'icon': '📊',
     'desc': 'Create stunning presentations', 'color': '#6366f1'},
    {'id': 'sheet-studio', 'name': 'Sheet Studio', 'icon': '📋',
     'desc': 'Intelligent spreadsheets', 'color': '#10b981'},
    {'id': 'text-prompter', 'name': 'Text Prompter', 'icon': '✍️',
     'desc': 'AI writing assistant', 'color': '#a78bfa'},
    {'id': 'horizon-teams', 'name': 'Horizon Teams', 'icon': '👥',
     'desc': 'Team collaboration', 'color': '#3b82f6'},
    {'id': 'dev-studio', 'name': 'Dev Studio', 'icon': '🛠️',
     'desc': 'Build apps with AI', 'color': '#f59e0b'},
]


# ─── Settings API Bridge (pywebview) ─────────────────
class SettingsAPI:
    """JS bridge for the HTML settings app"""
    def __init__(self, desktop):
        self.desktop = desktop

    def get_config(self):
        return self.desktop.config.get('theme_tweaks', {})

    def set_color(self, key, value):
        self.desktop.config.setdefault('theme_tweaks', {})[key] = value
        save_config(self.desktop.config)
        # Live update
        self.desktop.root.after(0, lambda: self.desktop._apply_live_color(key, value))

    def set_slider(self, key, value):
        self.desktop.config.setdefault('theme_tweaks', {})[key] = int(value)
        save_config(self.desktop.config)
        # Live updates for key layout values
        if key == 'taskbar_opacity':
            self.desktop.root.after(0, lambda: self.desktop._live_opacity('taskbar', int(value)/100))
        elif key == 'taskbar_height':
            self.desktop.root.after(0, self.desktop._live_taskbar_height)
        elif key in ('prompt_width', 'prompt_height', 'prompt_offset'):
            self.desktop.root.after(0, self.desktop._live_prompt_size)

    def apply_font(self, font_name):
        self.desktop.config.setdefault('theme_tweaks', {})['font_family'] = font_name
        save_config(self.desktop.config)
        self.desktop.root.after(0, lambda: self.desktop._apply_font_live(font_name))

    def reset_layout(self):
        self.desktop.root.after(0, self.desktop._reset_layout)

    def browse_wallpaper(self):
        def do_browse():
            from tkinter import filedialog
            path = filedialog.askopenfilename(
                title="Select Wallpaper",
                filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
            )
            if path:
                ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, path, 0x01 | 0x02)
        self.desktop.root.after(0, do_browse)

    def restore_wallpaper(self):
        pass  # Will restore from backup

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
            except Exception as ex:
                print(f'  ⚠ Icon apply: {ex}')
        threading.Thread(target=do_apply, daemon=True).start()

    def restore_default_icons(self):
        def do_restore():
            try:
                sys.path.insert(0, SCRIPT_DIR)
                import icon_manager
                icon_manager.restore_default_icons()
            except Exception as ex:
                print(f'  ⚠ Restore: {ex}')
        threading.Thread(target=do_restore, daemon=True).start()

    def close_settings(self):
        if hasattr(self.desktop, '_settings_webview') and self.desktop._settings_webview:
            self.desktop._settings_webview.destroy()
            self.desktop._settings_webview = None


# ─── Windows API ─────────────────────────────────────
class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("hWnd", ctypes.wintypes.HWND),
        ("uCallbackMessage", ctypes.wintypes.UINT),
        ("uEdge", ctypes.wintypes.UINT),
        ("rc", ctypes.wintypes.RECT),
        ("lParam", ctypes.wintypes.LPARAM),
    ]


# ═══════════════════════════════════════════════════════
#   HORIZON DESKTOP — Main Controller
# ═══════════════════════════════════════════════════════
class HorizonDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide root — we only use Toplevels

        self.sw = user32.GetSystemMetrics(0)
        self.sh = user32.GetSystemMetrics(1)

        self.config = load_config()
        tweaks = self.config.get('theme_tweaks', {})
        self.taskbar_h = int(tweaks.get('taskbar_height', 36))
        self.prompt_w = int(tweaks.get('prompt_width', 640))
        self.prompt_h = int(tweaks.get('prompt_height', 50))

        self.running = True
        self.icon_cache = {}
        self.appbar_registered = False

        # Build desktop elements
        self._create_taskbar()
        self._create_prompt()
        self._reserve_screen_space()

        # Start window tracking
        if win32gui:
            self._start_window_tracking()

        # Clock
        self._update_time()

        # Start backend
        self.backend = self._start_backend()
        atexit.register(self._cleanup)

        # Hide Windows taskbar
        self._hide_win_taskbar()

    # ─── Backend ─────────────────────────────────────
    def _start_backend(self):
        backend_script = os.path.join(SCRIPT_DIR, 'backend.py')
        if os.path.exists(backend_script):
            return subprocess.Popen(
                [sys.executable, backend_script],
                cwd=SCRIPT_DIR,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        return None

    # ─── Windows Taskbar ─────────────────────────────
    def _hide_win_taskbar(self):
        hwnd = user32.FindWindowW("Shell_TrayWnd", None)
        if hwnd:
            user32.ShowWindow(hwnd, 0)

    def _show_win_taskbar(self):
        hwnd = user32.FindWindowW("Shell_TrayWnd", None)
        if hwnd:
            user32.ShowWindow(hwnd, 5)

    # ─── AppBar ──────────────────────────────────────
    def _reserve_screen_space(self):
        try:
            hwnd = int(self.taskbar.winfo_id())
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(APPBARDATA)
            abd.hWnd = hwnd
            abd.uCallbackMessage = 0x0401
            abd.uEdge = 1
            abd.rc.left = 0
            abd.rc.top = 0
            abd.rc.right = self.sw
            abd.rc.bottom = self.taskbar_h
            shell32.SHAppBarMessage(0, ctypes.byref(abd))
            shell32.SHAppBarMessage(3, ctypes.byref(abd))
            self.appbar_registered = True
        except:
            pass

    def _release_screen_space(self):
        if self.appbar_registered:
            try:
                hwnd = int(self.taskbar.winfo_id())
                abd = APPBARDATA()
                abd.cbSize = ctypes.sizeof(APPBARDATA)
                abd.hWnd = hwnd
                shell32.SHAppBarMessage(1, ctypes.byref(abd))
            except:
                pass

    # ═══════════════════════════════════════════════════
    #   TASKBAR  — Thin glassmorphic strip at top
    # ═══════════════════════════════════════════════════
    def _create_taskbar(self):
        self.taskbar = tk.Toplevel(self.root)
        self.taskbar.overrideredirect(True)
        self.taskbar.attributes('-topmost', True)
        self.taskbar.attributes('-alpha', 0.94)
        self.taskbar.geometry(f"{self.sw}x{self.taskbar_h}+0+0")
        self.taskbar.configure(bg=Colors.BG_GLASS)

        # Hide from Alt+Tab
        if win32gui:
            hwnd = int(self.taskbar.winfo_id())
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   style | win32con.WS_EX_TOOLWINDOW)

        # Accent line at bottom
        tk.Frame(self.taskbar, bg=Colors.ACCENT_DIM, height=1).pack(
            side=tk.BOTTOM, fill=tk.X)

        # Main content frame
        content = tk.Frame(self.taskbar, bg=Colors.BG_GLASS)
        content.pack(fill=tk.BOTH, expand=True)

        # LEFT — Horizon branding (clickable → app launcher)
        left = tk.Frame(content, bg=Colors.BG_GLASS, cursor='hand2')
        left.pack(side=tk.LEFT, padx=16)

        star = tk.Label(left, text="✦", font=('Segoe UI Symbol', 11),
                 fg=Colors.ACCENT_LIGHT, bg=Colors.BG_GLASS)
        star.pack(side=tk.LEFT)
        brand = tk.Label(left, text="Horizon", font=('Segoe UI', 12, 'bold'),
                 fg=Colors.TEXT, bg=Colors.BG_GLASS)
        brand.pack(side=tk.LEFT, padx=(5, 0))

        # Click handlers for app launcher
        for w in (left, star, brand):
            w.bind('<Button-1>', lambda e: self._toggle_app_launcher())
            w.bind('<Enter>', lambda e: star.config(fg=Colors.ACCENT))
            w.bind('<Leave>', lambda e: star.config(fg=Colors.ACCENT_LIGHT))

        # CENTER — Running apps
        self.apps_frame = tk.Frame(content, bg=Colors.BG_GLASS)
        self.apps_frame.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        # RIGHT — Time + controls
        right = tk.Frame(content, bg=Colors.BG_GLASS)
        right.pack(side=tk.RIGHT, padx=16)

        # Settings button
        settings_btn = tk.Label(right, text="⚙", font=('Segoe UI', 12),
                                fg=Colors.TEXT_MUTED, bg=Colors.BG_GLASS,
                                cursor='hand2')
        settings_btn.pack(side=tk.RIGHT, padx=8)
        settings_btn.bind('<Button-1>', lambda e: self._toggle_settings())
        settings_btn.bind('<Enter>', lambda e: settings_btn.config(fg=Colors.TEXT))
        settings_btn.bind('<Leave>', lambda e: settings_btn.config(fg=Colors.TEXT_MUTED))

        # Time
        self.time_label = tk.Label(right, text="", font=('Segoe UI', 11, 'bold'),
                                   fg=Colors.TEXT, bg=Colors.BG_GLASS)
        self.time_label.pack(side=tk.RIGHT, padx=4)

        self.date_label = tk.Label(right, text="", font=('Segoe UI', 10),
                                   fg=Colors.TEXT_MUTED, bg=Colors.BG_GLASS)
        self.date_label.pack(side=tk.RIGHT, padx=4)

        # Separator dot
        tk.Label(right, text="·", font=('Segoe UI', 10),
                 fg=Colors.TEXT_DIM, bg=Colors.BG_GLASS
                 ).pack(side=tk.RIGHT, padx=2)

        # Close button
        close_btn = tk.Label(right, text="✕", font=('Segoe UI', 10),
                             fg=Colors.TEXT_DIM, bg=Colors.BG_GLASS,
                             cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=8)
        close_btn.bind('<Button-1>', lambda e: self._exit())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=Colors.CLOSE_RED))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=Colors.TEXT_DIM))

    # ═══════════════════════════════════════════════════
    #   PROMPT  — Floating rounded pill at bottom
    # ═══════════════════════════════════════════════════
    def _create_prompt(self):
        w = self.prompt_w
        h = self.prompt_h

        self.prompt = tk.Toplevel(self.root)
        self.prompt.overrideredirect(True)
        self.prompt.attributes('-topmost', True)
        self.prompt.attributes('-alpha', 0.96)

        x = (self.sw - w) // 2
        y = self.sh - h - 20

        self.prompt.geometry(f"{w}x{h}+{x}+{y}")
        self.prompt.configure(bg=Colors.TRANSPARENT)
        self.prompt.wm_attributes("-transparentcolor", Colors.TRANSPARENT)

        # Canvas for rounded corners
        self.prompt_canvas = tk.Canvas(self.prompt, width=w, height=h,
                                       bg=Colors.TRANSPARENT, highlightthickness=0)
        self.prompt_canvas.pack(fill=tk.BOTH, expand=True)

        # Draw rounded rectangle
        r = 24  # corner radius
        c = Colors.PROMPT_BG
        b = Colors.BORDER

        # Corners (arcs)
        self.prompt_canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=c, outline=b, width=1)
        self.prompt_canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=c, outline=b, width=1)
        self.prompt_canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=c, outline=b, width=1)
        self.prompt_canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=c, outline=b, width=1)

        # Fill rectangles
        self.prompt_canvas.create_rectangle(r, 0, w-r, h+1, fill=c, outline="")
        self.prompt_canvas.create_rectangle(0, r, w+1, h-r, fill=c, outline="")

        # Border lines (top + bottom edges)
        self.prompt_canvas.create_line(r, 0, w-r, 0, fill=b)
        self.prompt_canvas.create_line(r, h-1, w-r, h-1, fill=b)

        # Content container
        container = tk.Frame(self.prompt, bg=Colors.PROMPT_BG)
        container.place(x=r, y=6, width=w-2*r, height=h-12)

        # Star icon
        tk.Label(container, text="✦", font=('Segoe UI Symbol', 13),
                 fg=Colors.ACCENT_LIGHT, bg=Colors.PROMPT_BG
                 ).pack(side=tk.LEFT, padx=(4, 10))

        # Text input
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(container, textvariable=self.input_var,
                              font=('Segoe UI Variable Display', 13),
                              fg=Colors.TEXT, bg=Colors.PROMPT_BG,
                              insertbackground=Colors.ACCENT,
                              relief=tk.FLAT, bd=0)
        self.entry.insert(0, "Ask anything...")
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry.bind('<FocusIn>', self._on_focus)
        self.entry.bind('<FocusOut>', self._on_blur)
        self.entry.bind('<Return>', self._on_submit)

        # Send button (circle)
        send_canvas = tk.Canvas(container, width=34, height=34,
                                bg=Colors.PROMPT_BG, highlightthickness=0)
        send_canvas.pack(side=tk.RIGHT, padx=(8, 4))
        send_canvas.create_oval(2, 2, 32, 32, fill=Colors.SEND_BG, outline="")
        send_canvas.create_text(17, 17, text="→", fill='white',
                                font=('Segoe UI', 13, 'bold'))
        send_canvas.bind('<Button-1>', self._on_submit)

    # ─── Input Events ────────────────────────────────
    def _on_focus(self, e):
        if self.entry.get() == "Ask anything...":
            self.entry.delete(0, tk.END)
            self.entry.config(fg=Colors.TEXT)

    def _on_blur(self, e):
        if not self.entry.get().strip():
            self.entry.insert(0, "Ask anything...")
            self.entry.config(fg=Colors.TEXT_MUTED)

    def _on_submit(self, e=None):
        text = self.input_var.get().strip()
        if not text or text == "Ask anything...":
            return
        if text == '@settings':
            self._toggle_settings()
        else:
            # Send to backend via HTTP
            self._send_query(text)
        self.input_var.set("")

    def _send_query(self, text):
        """Send query to backend API"""
        def do_send():
            try:
                import urllib.request
                data = json.dumps({"type": "query", "data": text}).encode()
                req = urllib.request.Request(
                    f"http://127.0.0.1:{BACKEND_PORT}/api/query",
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                urllib.request.urlopen(req, timeout=5)
            except:
                pass
        threading.Thread(target=do_send, daemon=True).start()

    # ─── Time ────────────────────────────────────────
    def _update_time(self):
        if not self.running:
            return
        from datetime import datetime
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M"))
        self.date_label.config(text=now.strftime("%a, %b %d"))
        self.root.after(10000, self._update_time)

    # ─── Window Tracking ─────────────────────────────
    def _start_window_tracking(self):
        def track():
            while self.running:
                try:
                    self.root.after(0, self._update_apps)
                except:
                    pass
                time.sleep(3)
        threading.Thread(target=track, daemon=True).start()

    def _update_apps(self):
        if not win32gui:
            return
        apps = []
        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title or title in ('', 'Program Manager', 'MSCTFIME UI',
                                       'Default IME', 'Horizon'):
                return
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                name = proc.name().lower()
                if 'python' in name or 'node' in name:
                    return
            except:
                pass
            apps.append({'hwnd': hwnd, 'title': title})
        try:
            win32gui.EnumWindows(callback, None)
        except:
            pass
        self._refresh_app_icons(apps)

    def _refresh_app_icons(self, apps):
        # Clear old icons
        for w in self.apps_frame.winfo_children():
            w.destroy()

        for app in apps[:10]:  # Max 10 apps
            frame = tk.Frame(self.apps_frame, bg=Colors.BG_GLASS, cursor='hand2')
            frame.pack(side=tk.LEFT, padx=2)

            label = tk.Label(frame, text=app['title'][:14],
                             font=('Segoe UI', 10),
                             fg=Colors.TEXT_MUTED, bg=Colors.BG_GLASS,
                             padx=8, pady=2)
            label.pack()

            hwnd = app['hwnd']
            frame.bind('<Button-1>', lambda e, h=hwnd: self._activate_window(h))
            label.bind('<Button-1>', lambda e, h=hwnd: self._activate_window(h))
            frame.bind('<Enter>', lambda e, l=label: l.config(fg=Colors.TEXT))
            frame.bind('<Leave>', lambda e, l=label: l.config(fg=Colors.TEXT_MUTED))

    def _activate_window(self, hwnd):
        try:
            if win32gui:
                win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                win32gui.SetForegroundWindow(hwnd)
        except:
            pass

    # ═══════════════════════════════════════════════════
    #   APP LAUNCHER — Dropdown from Horizon logo
    # ═══════════════════════════════════════════════════
    def _toggle_app_launcher(self):
        if hasattr(self, '_app_launcher') and self._app_launcher.winfo_exists():
            self._app_launcher.destroy()
            return

        W = 280
        H = len(HORIZON_APPS) * 52 + 16
        x = 16
        y = self.taskbar_h + 4

        self._app_launcher = tk.Toplevel(self.root)
        self._app_launcher.overrideredirect(True)
        self._app_launcher.attributes('-topmost', True)
        self._app_launcher.attributes('-alpha', 0.97)
        self._app_launcher.geometry(f"{W}x{H}+{x}+{y}")
        self._app_launcher.configure(bg=Colors.BG_CARD)

        if win32gui:
            hwnd = int(self._app_launcher.winfo_id())
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   style | win32con.WS_EX_TOOLWINDOW)

        # Header
        hdr = tk.Frame(self._app_launcher, bg=Colors.BG_GLASS, height=32)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="✦ Horizon Apps", font=('Segoe UI', 10, 'bold'),
                 fg=Colors.TEXT, bg=Colors.BG_GLASS).pack(side=tk.LEFT, padx=12)

        # App list
        for app in HORIZON_APPS:
            row = tk.Frame(self._app_launcher, bg=Colors.BG_CARD,
                           cursor='hand2', padx=12, pady=6)
            row.pack(fill=tk.X)

            icon_lbl = tk.Label(row, text=app['icon'], font=('Segoe UI', 16),
                                bg=Colors.BG_CARD)
            icon_lbl.pack(side=tk.LEFT, padx=(0, 10))

            info = tk.Frame(row, bg=Colors.BG_CARD)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)

            name_lbl = tk.Label(info, text=app['name'], font=('Segoe UI', 11),
                                fg=Colors.TEXT, bg=Colors.BG_CARD, anchor='w')
            name_lbl.pack(fill=tk.X)

            desc_lbl = tk.Label(info, text=app['desc'], font=('Segoe UI', 9),
                                fg=Colors.TEXT_DIM, bg=Colors.BG_CARD, anchor='w')
            desc_lbl.pack(fill=tk.X)

            # Hover effects
            def on_enter(e, r=row):
                r.config(bg=Colors.BG_GLASS_LIGHT)
                for w in r.winfo_children():
                    try: w.config(bg=Colors.BG_GLASS_LIGHT)
                    except: pass
                    for c in w.winfo_children():
                        try: c.config(bg=Colors.BG_GLASS_LIGHT)
                        except: pass

            def on_leave(e, r=row):
                r.config(bg=Colors.BG_CARD)
                for w in r.winfo_children():
                    try: w.config(bg=Colors.BG_CARD)
                    except: pass
                    for c in w.winfo_children():
                        try: c.config(bg=Colors.BG_CARD)
                        except: pass

            app_id = app['id']
            for w in (row, icon_lbl, info, name_lbl, desc_lbl):
                w.bind('<Button-1>', lambda e, aid=app_id: self._open_horizon_app(aid))
                w.bind('<Enter>', on_enter)
                w.bind('<Leave>', on_leave)

        # Auto-close when clicking elsewhere
        self._app_launcher.bind('<FocusOut>', lambda e: self._close_app_launcher())

    def _close_app_launcher(self):
        if hasattr(self, '_app_launcher') and self._app_launcher.winfo_exists():
            self._app_launcher.destroy()

    def _open_horizon_app(self, app_id):
        """Open a Horizon app via pywebview subprocess"""
        self._close_app_launcher()
        app_html = os.path.join(APPS_DIR, app_id, 'index.html')
        if not os.path.exists(app_html):
            print(f"  \u26a0 App not found: {app_html}")
            return

        app_info = next((a for a in HORIZON_APPS if a['id'] == app_id), None)
        title = app_info['name'] if app_info else app_id

        webview_script = os.path.join(SCRIPT_DIR, 'open_webview.py')
        if os.path.exists(webview_script):
            subprocess.Popen(
                [sys.executable, webview_script, app_html, f'Horizon {title}', '800', '560'],
                cwd=SCRIPT_DIR
            )
        else:
            import webbrowser
            webbrowser.open(f'file:///{app_html}')

    # ═══════════════════════════════════════════════════
    #   SETTINGS — HTML/CSS/JS via pywebview
    # ═══════════════════════════════════════════════════
    def _toggle_settings(self):
        # If pywebview available, use HTML settings
        if webview:
            self._open_html_settings()
            return
        # Fallback to Tkinter settings
        self._toggle_tkinter_settings()

    def _open_html_settings(self):
        """Open React settings app via pywebview subprocess"""
        settings_html = os.path.join(APPS_DIR, 'settings', 'dist', 'index.html')
        if not os.path.exists(settings_html):
            print(f"  \u26a0 Settings app not found: {settings_html}")
            return

        settings_script = os.path.join(SCRIPT_DIR, 'open_settings_webview.py')
        if os.path.exists(settings_script):
            subprocess.Popen(
                [sys.executable, settings_script, settings_html],
                cwd=SCRIPT_DIR
            )
        else:
            import webbrowser
            webbrowser.open(f'file:///{settings_html}')

    def _apply_font_live(self, font_name):
        """Apply font change live to UI elements"""
        self.time_label.config(font=(font_name, 11, 'bold'))
        self.date_label.config(font=(font_name, 10))
        self.entry.config(font=(font_name, 13))

    def _toggle_tkinter_settings(self):
        """Fallback Tkinter settings if pywebview not available"""
        if hasattr(self, 'settings_win') and self.settings_win.winfo_exists():
            self.settings_win.destroy()
            return

        W, H = 560, 500
        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.overrideredirect(True)
        self.settings_win.attributes('-topmost', True)
        self.settings_win.attributes('-alpha', 0.97)
        self.settings_win.geometry(f"{W}x{H}+{(self.sw-W)//2}+{(self.sh-H)//2}")
        self.settings_win.configure(bg=Colors.BG_CARD)

        # Hide from Alt+Tab
        if win32gui:
            hwnd = int(self.settings_win.winfo_id())
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   style | win32con.WS_EX_TOOLWINDOW)

        # ── Header
        header = tk.Frame(self.settings_win, bg=Colors.BG_GLASS, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="⚙  Settings", font=('Segoe UI', 12, 'bold'),
                 fg=Colors.TEXT, bg=Colors.BG_GLASS).pack(side=tk.LEFT, padx=16)

        close = tk.Label(header, text="✕", font=('Segoe UI', 11),
                         fg=Colors.TEXT_DIM, bg=Colors.BG_GLASS, cursor='hand2')
        close.pack(side=tk.RIGHT, padx=12)
        close.bind('<Button-1>', lambda e: self.settings_win.destroy())
        close.bind('<Enter>', lambda e: close.config(fg=Colors.CLOSE_RED))
        close.bind('<Leave>', lambda e: close.config(fg=Colors.TEXT_DIM))

        # ── Tab bar
        tab_bar = tk.Frame(self.settings_win, bg=Colors.BG_GLASS_LIGHT, height=34)
        tab_bar.pack(fill=tk.X)
        tab_bar.pack_propagate(False)

        self._settings_tabs = {}
        self._settings_tab_btns = {}
        self._settings_body = tk.Frame(self.settings_win, bg=Colors.BG_CARD)
        self._settings_body.pack(fill=tk.BOTH, expand=True)

        tabs = [
            ('appearance', '🎨 Appearance'),
            ('wallpaper', '🖼 Wallpaper'),
            ('typography', '🔤 Typography'),
            ('layout', '📐 Layout'),
            ('icons', '🎯 Icon Studio'),
        ]

        for key, label in tabs:
            btn = tk.Label(tab_bar, text=label, font=('Segoe UI', 9),
                           fg=Colors.TEXT_MUTED, bg=Colors.BG_GLASS_LIGHT,
                           padx=12, pady=6, cursor='hand2')
            btn.pack(side=tk.LEFT)
            btn.bind('<Button-1>', lambda e, k=key: self._show_settings_tab(k))
            self._settings_tab_btns[key] = btn

        # Build tab contents
        self._build_appearance_tab()
        self._build_wallpaper_tab()
        self._build_typography_tab()
        self._build_layout_tab()
        self._build_icon_studio_tab()

        # Show first tab
        self._show_settings_tab('appearance')

    def _show_settings_tab(self, key):
        # Hide all tabs
        for frame in self._settings_tabs.values():
            frame.pack_forget()
        # Reset button styles
        for btn in self._settings_tab_btns.values():
            btn.config(fg=Colors.TEXT_MUTED, bg=Colors.BG_GLASS_LIGHT)
        # Show selected
        self._settings_tabs[key].pack(fill=tk.BOTH, expand=True)
        self._settings_tab_btns[key].config(fg=Colors.TEXT, bg=Colors.BG_CARD)

    # ── Tab: Appearance ──────────────────────────────
    def _build_appearance_tab(self):
        f = tk.Frame(self._settings_body, bg=Colors.BG_CARD, padx=24, pady=16)
        self._settings_tabs['appearance'] = f

        cfg = self.config.get('theme_tweaks', {})

        # Helper: color row
        def color_row(parent, label_text, config_key, default):
            row = tk.Frame(parent, bg=Colors.BG_CARD)
            row.pack(fill=tk.X, pady=6)
            tk.Label(row, text=label_text, font=('Segoe UI', 10),
                     fg=Colors.TEXT, bg=Colors.BG_CARD, width=18, anchor='w').pack(side=tk.LEFT)
            swatch = tk.Canvas(row, width=28, height=28, bg=Colors.BG_CARD,
                               highlightthickness=0, cursor='hand2')
            swatch.pack(side=tk.RIGHT, padx=4)
            color = cfg.get(config_key, default)
            swatch.create_rectangle(2, 2, 26, 26, fill=color, outline=Colors.BORDER, width=1)
            def pick(e, ck=config_key, sw=swatch):
                from tkinter import colorchooser
                result = colorchooser.askcolor(title=f"Pick {label_text}")
                if result and result[1]:
                    hex_color = result[1]
                    sw.delete('all')
                    sw.create_rectangle(2, 2, 26, 26, fill=hex_color, outline=Colors.BORDER, width=1)
                    self.config.setdefault('theme_tweaks', {})[ck] = hex_color
                    save_config(self.config)
                    self._apply_live_color(ck, hex_color)
            swatch.bind('<Button-1>', pick)
            return row

        color_row(f, "Accent Color", "accent_color", Colors.ACCENT)
        color_row(f, "Text Color", "text_color", Colors.TEXT)
        color_row(f, "Panel Background", "panel_bg", Colors.BG_GLASS)
        color_row(f, "App Icon Color", "app_icon_color", Colors.TEXT_MUTED)

        # Separator
        tk.Frame(f, bg=Colors.BORDER, height=1).pack(fill=tk.X, pady=10)

        # Taskbar Opacity
        tk.Label(f, text="Taskbar Opacity", font=('Segoe UI', 10),
                 fg=Colors.TEXT, bg=Colors.BG_CARD).pack(anchor=tk.W)
        opacity_scale = tk.Scale(f, from_=50, to=100, orient=tk.HORIZONTAL,
                                 bg=Colors.BG_CARD, fg=Colors.TEXT,
                                 troughcolor=Colors.BG_GLASS, highlightthickness=0,
                                 sliderrelief=tk.FLAT, activebackground=Colors.ACCENT,
                                 command=lambda v: self._live_opacity('taskbar', int(v)/100))
        opacity_scale.set(int(cfg.get('taskbar_opacity', 94)))
        opacity_scale.pack(fill=tk.X, pady=(0, 4))

        # App Icon Opacity
        tk.Label(f, text="App Icon Opacity", font=('Segoe UI', 10),
                 fg=Colors.TEXT, bg=Colors.BG_CARD).pack(anchor=tk.W)
        icon_op = tk.Scale(f, from_=30, to=100, orient=tk.HORIZONTAL,
                           bg=Colors.BG_CARD, fg=Colors.TEXT,
                           troughcolor=Colors.BG_GLASS, highlightthickness=0,
                           sliderrelief=tk.FLAT, activebackground=Colors.ACCENT,
                           command=lambda v: self._save_tweak('app_icon_opacity', int(v)))
        icon_op.set(int(cfg.get('app_icon_opacity', 70)))
        icon_op.pack(fill=tk.X)

    def _apply_live_color(self, key, color):
        """Apply color changes live"""
        if key == 'panel_bg':
            self.taskbar.configure(bg=color)
            for w in self.taskbar.winfo_children():
                try: w.configure(bg=color)
                except: pass
        elif key == 'accent_color':
            Colors.ACCENT = color
        elif key == 'text_color':
            self.time_label.config(fg=color)

    def _live_opacity(self, panel, value):
        """Live opacity update"""
        if panel == 'taskbar':
            self.taskbar.attributes('-alpha', value)
            self._save_tweak('taskbar_opacity', int(value * 100))

    def _save_tweak(self, key, value):
        self.config.setdefault('theme_tweaks', {})[key] = value
        save_config(self.config)

    # ── Tab: Wallpaper ───────────────────────────────
    def _build_wallpaper_tab(self):
        f = tk.Frame(self._settings_body, bg=Colors.BG_CARD, padx=24, pady=16)
        self._settings_tabs['wallpaper'] = f

        tk.Label(f, text="Desktop Wallpaper", font=('Segoe UI', 11, 'bold'),
                 fg=Colors.TEXT, bg=Colors.BG_CARD).pack(anchor=tk.W, pady=(0, 8))

        # Wallpaper grid
        grid = tk.Frame(f, bg=Colors.BG_CARD)
        grid.pack(fill=tk.BOTH, expand=True)

        # Load wallpapers
        wallpaper_dir = os.path.join(PROJECT_ROOT, 'wallpapers')
        os.makedirs(wallpaper_dir, exist_ok=True)

        wallpapers = []
        if os.path.isdir(wallpaper_dir):
            for fn in os.listdir(wallpaper_dir):
                if fn.lower().endswith(('.jpg','.jpeg','.png','.bmp')):
                    wallpapers.append(os.path.join(wallpaper_dir, fn))

        self._wp_thumbs = []  # keep references
        col = 0
        row_f = tk.Frame(grid, bg=Colors.BG_CARD)
        row_f.pack(fill=tk.X, pady=4)

        from PIL import Image, ImageTk
        for i, wp in enumerate(wallpapers[:12]):
            try:
                img = Image.open(wp).resize((100, 65), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self._wp_thumbs.append(tk_img)
                lbl = tk.Label(row_f, image=tk_img, bg=Colors.BG_CARD,
                               cursor='hand2', bd=2, relief=tk.FLAT)
                lbl.grid(row=i//4, column=i%4, padx=4, pady=4)
                lbl.bind('<Button-1>', lambda e, p=wp: self._set_wallpaper(p))
            except:
                pass

        # Browse button
        browse = tk.Label(f, text="  📁 Browse...  ", font=('Segoe UI', 10),
                          fg=Colors.TEXT, bg=Colors.BG_GLASS_LIGHT,
                          padx=12, pady=6, cursor='hand2')
        browse.pack(anchor=tk.W, pady=8)
        browse.bind('<Button-1>', lambda e: self._browse_wallpaper())

    def _set_wallpaper(self, path):
        try:
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, path, 0x01 | 0x02)
        except:
            pass

    def _browse_wallpaper(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select Wallpaper",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
        )
        if path:
            self._set_wallpaper(path)

    # ── Tab: Typography ──────────────────────────────
    def _build_typography_tab(self):
        f = tk.Frame(self._settings_body, bg=Colors.BG_CARD, padx=24, pady=16)
        self._settings_tabs['typography'] = f

        tk.Label(f, text="Font Family", font=('Segoe UI', 11, 'bold'),
                 fg=Colors.TEXT, bg=Colors.BG_CARD).pack(anchor=tk.W, pady=(0, 6))

        # Font list
        list_frame = tk.Frame(f, bg=Colors.BG_GLASS)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.font_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10),
                                        fg=Colors.TEXT, bg=Colors.BG_GLASS_LIGHT,
                                        selectbackground=Colors.ACCENT,
                                        selectforeground='white',
                                        highlightthickness=0, bd=0,
                                        yscrollcommand=scrollbar.set)
        self.font_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.font_listbox.yview)

        # Populate fonts
        try:
            fonts = sorted(set(tkfont.families()))
            current_font = self.config.get('theme_tweaks', {}).get('font_family', 'Segoe UI')
            for i, name in enumerate(fonts):
                self.font_listbox.insert(tk.END, name)
                if name == current_font:
                    self.font_listbox.selection_set(i)
                    self.font_listbox.see(i)
        except:
            pass

        # Preview
        self.font_preview = tk.Label(f, text="The quick brown fox jumps over the lazy dog",
                                     font=('Segoe UI', 12), fg=Colors.TEXT,
                                     bg=Colors.BG_GLASS_LIGHT, pady=8, padx=12)
        self.font_preview.pack(fill=tk.X, pady=(8, 4))

        self.font_listbox.bind('<<ListboxSelect>>', self._on_font_preview)

        # Apply button
        apply_btn = tk.Label(f, text="  Apply Font  ", font=('Segoe UI', 10, 'bold'),
                             fg='white', bg=Colors.SEND_BG, padx=12, pady=6, cursor='hand2')
        apply_btn.pack(anchor=tk.E, pady=4)
        apply_btn.bind('<Button-1>', lambda e: self._apply_font())

    def _on_font_preview(self, e):
        sel = self.font_listbox.curselection()
        if sel:
            font_name = self.font_listbox.get(sel[0])
            self.font_preview.config(font=(font_name, 12))

    def _apply_font(self):
        sel = self.font_listbox.curselection()
        if sel:
            font_name = self.font_listbox.get(sel[0])
            self._save_tweak('font_family', font_name)
            # Live update
            self.time_label.config(font=(font_name, 11, 'bold'))
            self.date_label.config(font=(font_name, 10))
            self.entry.config(font=(font_name, 13))

    # ── Tab: Layout ──────────────────────────────────
    def _build_layout_tab(self):
        f = tk.Frame(self._settings_body, bg=Colors.BG_CARD, padx=24, pady=16)
        self._settings_tabs['layout'] = f

        cfg = self.config.get('theme_tweaks', {})

        def slider_row(parent, label, from_, to, default, config_key, live_fn=None):
            tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold'),
                     fg=Colors.TEXT, bg=Colors.BG_CARD).pack(anchor=tk.W, pady=(8, 0))
            s = tk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL,
                         bg=Colors.BG_CARD, fg=Colors.TEXT,
                         troughcolor=Colors.BG_GLASS, highlightthickness=0,
                         sliderrelief=tk.FLAT, activebackground=Colors.ACCENT,
                         command=lambda v: self._on_layout_change(config_key, int(v), live_fn))
            s.set(int(cfg.get(config_key, default)))
            s.pack(fill=tk.X, pady=(0, 4))

        slider_row(f, "Taskbar Height", 28, 52, 36, 'taskbar_height', self._live_taskbar_height)
        slider_row(f, "Prompt Width", 400, 900, 640, 'prompt_width', self._live_prompt_size)
        slider_row(f, "Prompt Height", 40, 70, 50, 'prompt_height', self._live_prompt_size)
        slider_row(f, "Prompt Bottom Offset", 10, 80, 20, 'prompt_offset', self._live_prompt_size)

        # Reset button
        reset = tk.Label(f, text="  Reset to Defaults  ", font=('Segoe UI', 10),
                         fg=Colors.TEXT, bg=Colors.BG_GLASS_LIGHT,
                         padx=12, pady=6, cursor='hand2')
        reset.pack(anchor=tk.W, pady=12)
        reset.bind('<Button-1>', lambda e: self._reset_layout())

    def _on_layout_change(self, key, value, live_fn=None):
        self._save_tweak(key, value)
        if live_fn:
            live_fn()

    def _live_taskbar_height(self):
        h = self.config.get('theme_tweaks', {}).get('taskbar_height', 36)
        self.taskbar.geometry(f"{self.sw}x{h}+0+0")

    def _live_prompt_size(self):
        cfg = self.config.get('theme_tweaks', {})
        w = int(cfg.get('prompt_width', 640))
        h = int(cfg.get('prompt_height', 50))
        offset = int(cfg.get('prompt_offset', 20))
        x = (self.sw - w) // 2
        y = self.sh - h - offset
        self.prompt.geometry(f"{w}x{h}+{x}+{y}")

    def _reset_layout(self):
        defaults = {'taskbar_height': 36, 'prompt_width': 640,
                     'prompt_height': 50, 'prompt_offset': 20}
        self.config.setdefault('theme_tweaks', {}).update(defaults)
        save_config(self.config)
        self._live_taskbar_height()
        self._live_prompt_size()

    # ── Tab: Icon Design Studio ──────────────────────
    def _build_icon_studio_tab(self):
        f = tk.Frame(self._settings_body, bg=Colors.BG_CARD, padx=24, pady=12)
        self._settings_tabs['icons'] = f

        tk.Label(f, text="Icon Design Studio", font=('Segoe UI', 11, 'bold'),
                 fg=Colors.TEXT, bg=Colors.BG_CARD).pack(anchor=tk.W, pady=(0, 8))

        # Template selector
        templates_frame = tk.Frame(f, bg=Colors.BG_CARD)
        templates_frame.pack(fill=tk.X, pady=4)

        self._selected_template = tk.StringVar(value='gradient')

        template_names = {
            'gradient': '🌈 Gradient',
            'flat': '⬜ Flat',
            'neon': '💚 Neon',
            'pastel': '🩷 Pastel',
            'metallic': '⚙ Metallic',
            'glass': '🪟 Glass',
        }

        for key, label in template_names.items():
            rb = tk.Radiobutton(templates_frame, text=label,
                                variable=self._selected_template, value=key,
                                font=('Segoe UI', 9), fg=Colors.TEXT,
                                bg=Colors.BG_CARD, selectcolor=Colors.BG_GLASS_LIGHT,
                                activebackground=Colors.BG_CARD,
                                activeforeground=Colors.ACCENT_LIGHT,
                                highlightthickness=0,
                                command=self._preview_icon_template)
            rb.pack(side=tk.LEFT, padx=3)

        # Color picker for icon
        color_frame = tk.Frame(f, bg=Colors.BG_CARD)
        color_frame.pack(fill=tk.X, pady=8)

        tk.Label(color_frame, text="Icon Color:", font=('Segoe UI', 10),
                 fg=Colors.TEXT, bg=Colors.BG_CARD).pack(side=tk.LEFT)

        self._icon_color = Colors.ACCENT
        self._icon_swatch = tk.Canvas(color_frame, width=28, height=28,
                                       bg=Colors.BG_CARD, highlightthickness=0,
                                       cursor='hand2')
        self._icon_swatch.pack(side=tk.LEFT, padx=8)
        self._icon_swatch.create_rectangle(2, 2, 26, 26, fill=Colors.ACCENT,
                                            outline=Colors.BORDER, width=1, tags='swatch')
        self._icon_swatch.bind('<Button-1>', self._pick_icon_color)

        # Preview canvas
        tk.Label(f, text="Preview:", font=('Segoe UI', 9),
                 fg=Colors.TEXT_MUTED, bg=Colors.BG_CARD).pack(anchor=tk.W)
        self._icon_preview_canvas = tk.Canvas(f, width=128, height=128,
                                               bg=Colors.BG_GLASS_LIGHT,
                                               highlightthickness=1,
                                               highlightbackground=Colors.BORDER)
        self._icon_preview_canvas.pack(anchor=tk.W, pady=4)
        self._icon_preview_img = None

        # Action buttons
        btn_frame = tk.Frame(f, bg=Colors.BG_CARD)
        btn_frame.pack(fill=tk.X, pady=8)

        generate_btn = tk.Label(btn_frame, text="  Generate Preview  ",
                                font=('Segoe UI', 10),
                                fg=Colors.TEXT, bg=Colors.BG_GLASS_LIGHT,
                                padx=10, pady=5, cursor='hand2')
        generate_btn.pack(side=tk.LEFT, padx=4)
        generate_btn.bind('<Button-1>', lambda e: self._preview_icon_template())

        apply_btn = tk.Label(btn_frame, text="  Apply to All Folders  ",
                             font=('Segoe UI', 10, 'bold'),
                             fg='white', bg=Colors.SEND_BG,
                             padx=10, pady=5, cursor='hand2')
        apply_btn.pack(side=tk.LEFT, padx=4)
        apply_btn.bind('<Button-1>', lambda e: self._apply_icon_template())

        restore_btn = tk.Label(btn_frame, text="  Restore Defaults  ",
                               font=('Segoe UI', 10),
                               fg=Colors.TEXT_MUTED, bg=Colors.BG_GLASS,
                               padx=10, pady=5, cursor='hand2')
        restore_btn.pack(side=tk.LEFT, padx=4)
        restore_btn.bind('<Button-1>', lambda e: self._restore_default_icons())

    def _pick_icon_color(self, e=None):
        from tkinter import colorchooser
        result = colorchooser.askcolor(title="Pick Icon Color")
        if result and result[1]:
            self._icon_color = result[1]
            self._icon_swatch.delete('swatch')
            self._icon_swatch.create_rectangle(2, 2, 26, 26, fill=result[1],
                                                outline=Colors.BORDER, width=1, tags='swatch')

    def _preview_icon_template(self):
        """Generate and display icon preview"""
        def do_preview():
            try:
                sys.path.insert(0, SCRIPT_DIR)
                import icon_manager
                # Parse hex color to tuple
                hex_c = self._icon_color.lstrip('#')
                rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
                template = self._selected_template.get()
                png_path = icon_manager.get_template_preview(template, rgb)
                # Load into canvas
                from PIL import Image, ImageTk
                img = Image.open(png_path).resize((128, 128), Image.Resampling.LANCZOS)
                self._icon_preview_img = ImageTk.PhotoImage(img)
                self._icon_preview_canvas.delete('all')
                self._icon_preview_canvas.create_image(64, 64, image=self._icon_preview_img)
            except Exception as ex:
                print(f"  ⚠ Icon preview error: {ex}")
        threading.Thread(target=do_preview, daemon=True).start()

    def _apply_icon_template(self):
        """Generate icon and apply to all desktop folders"""
        def do_apply():
            try:
                sys.path.insert(0, SCRIPT_DIR)
                import icon_manager
                hex_c = self._icon_color.lstrip('#')
                rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
                template = self._selected_template.get()
                ico_path = icon_manager.create_icon_from_template(template, rgb)
                # Apply to all desktop folders
                from pathlib import Path
                desktop = Path.home() / "Desktop"
                for folder in desktop.iterdir():
                    if folder.is_dir() and not folder.name.startswith('.'):
                        icon_manager.apply_folder_icon(folder, ico_path)
                import ctypes
                ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
                print("  ✓ Icons applied to all desktop folders")
            except Exception as ex:
                print(f"  ⚠ Icon apply error: {ex}")
        threading.Thread(target=do_apply, daemon=True).start()

    def _restore_default_icons(self):
        """Restore default Windows folder icons"""
        def do_restore():
            try:
                sys.path.insert(0, SCRIPT_DIR)
                import icon_manager
                icon_manager.restore_default_icons()
                print("  ✓ Default icons restored")
            except Exception as ex:
                print(f"  ⚠ Restore error: {ex}")
        threading.Thread(target=do_restore, daemon=True).start()

    # ─── Cleanup ─────────────────────────────────────
    def _cleanup(self):
        self._release_screen_space()
        self._show_win_taskbar()
        if self.backend:
            try:
                self.backend.terminate()
            except:
                pass

    def _exit(self):
        self.running = False
        self._cleanup()
        self.root.quit()

    def run(self):
        print("\n  ✦ Horizon Desktop Theme Active")
        print("  ✦ Desktop elements created (not windows)")
        print("  ✦ Close from taskbar ✕ button\n")
        self.root.mainloop()


# ═══════════════════════════════════════════════════════
if __name__ == '__main__':
    app = HorizonDesktop()
    app.run()
