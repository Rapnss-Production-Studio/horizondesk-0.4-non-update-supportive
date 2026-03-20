
"""
Horizon Giga UI v9 - Premium Glassmorphism Edition
- Glassmorphism effects with blur and transparency
- Curved borders and smooth animations
- Dynamic gradient accents
- Connected to Omniagent via Bridge
"""

import tkinter as tk
from tkinter import ttk
import ctypes
from ctypes import wintypes, byref
import os
import subprocess
import json
import threading
import time
import sys
import re
import requests
from PIL import Image, ImageTk, ImageDraw
import win32gui
import win32con
import win32ui
import win32api
import win32process
import psutil
import queue

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import theme_manager
    import omni_bridge
except ImportError:
    # Fallback if running directly
    sys.path.append(os.path.dirname(__file__))
    import theme_manager
    import omni_bridge

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# Config paths
HORIZON_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'HorizonDesk')
CONFIG_FILE = os.path.join(HORIZON_DIR, 'config.json')

# Global bridge instance
OMNI_BRIDGE = None

def clean_ansi(text):
    """Remove ANSI escape sequences"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class LogWindow:
    """Semi-transparent window for Omniagent logs"""
    def __init__(self, root, theme_manager):
        self.root = root
        self.tm = theme_manager
        self.window = tk.Toplevel(root)
        self.window.title("Horizon Logs")
        self.window.withdraw()
        
        self.width = 500
        self.height = 300
        
        # Initial position (bottom right, above taskbar)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.x = screen_width - self.width - 20
        self.y = screen_height - 60 - self.height - 20
        
        self.window.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.90)
        self.window.overrideredirect(True)
        
        self.colors = self._get_colors()
        self.window.configure(bg=self.colors['bg_glass'])
        
        # Build UI
        self._build_ui()
        
    def _get_colors(self):
        return self.tm.get_theme_palette('light')
    
    def _build_ui(self):
        # Header
        header = tk.Frame(self.window, bg=self.colors['bg_glass'], height=30)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(header, text="Omniagent Logs", font=('Segoe UI', 9, 'bold'),
                 fg=self.colors['text'], bg=self.colors['bg_glass']).pack(side=tk.LEFT, padx=5)
        
        cls_btn = tk.Label(header, text="✕", fg=self.colors['text_muted'], bg=self.colors['bg_glass'], cursor='hand2')
        cls_btn.pack(side=tk.RIGHT, padx=5)
        cls_btn.bind('<Button-1>', lambda e: self.hide())
        
        # Log Text Area
        self.text_area = tk.Text(self.window, font=('Consolas', 9), bg=self.colors['bg_glass_light'],
                                 fg=self.colors['text'], relief=tk.FLAT, border=0, padx=10, pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.tag_config('user', foreground=self.colors['accent'])
        self.text_area.tag_config('agent', foreground=self.colors['text_secondary'])
        self.text_area.config(state=tk.DISABLED)
        
    def log(self, sender, message):
        self.text_area.config(state=tk.NORMAL)
        tag = 'user' if sender == 'User' else 'agent'
        timestamp = time.strftime("%H:%M:%S")
        
        # For streaming logs, we can just append.
        # But we want timestamps per line. 
        # Since we receive chunks, this is tricky. 
        # Simplified: Append raw chunk to log? Or buffer lines?
        # Let's just append raw chunk for now to see everything.
        
        self.text_area.insert(tk.END, message, tag)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
    
    def show(self):
        self.window.deiconify()
        self.window.lift()
        
    def hide(self):
        self.window.withdraw()
        
    def toggle(self):
        if self.window.winfo_viewable():
            self.hide()
        else:
            self.show()

class GigaUI:
    """Giga UI v9 - Premium Glassmorphism with curved borders"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        
        # Load Config & Tweaks
        self.config = self._load_config()
        tweaks = self.config.get('theme_tweaks', {})
        
        self.taskbar_height = int(tweaks.get('taskbar_height', 48))
        self.prompt_width = int(tweaks.get('prompt_width', 700))
        
        # Initialize Theme
        self.tm = theme_manager.ThemeManager()
        
        # Color Palette - Forced Light Mode per user request
        self.colors = self.tm.get_theme_palette('light')
        
        # Dynamic Fonts
        self.font_header = self.tm.get_font(13, 'bold')
        self.font_body = self.tm.get_font(10)
        self.font_prompt = self.tm.get_font(14)
        self.font_time = self.tm.get_font(12, 'bold')
        
        # Load Assets
        self.assets = {}
        self._load_assets()
        
        self.running = True
        self.icon_cache = {}
        self.exe_icon_cache = {}
        self.response_timer = None
        
        # Log Window
        self.log_window = LogWindow(self.root, self.tm)
        
        # Build UI
        self._create_taskbar()
        self._create_response_panel()
        self._create_prompt()
        
        self._reserve_screen_space()
        self._start_window_tracking()

        # Connect to OmniBridge (Streaming)
        self.msg_queue = queue.Queue()
        self._start_bridge()
        self.root.after(50, self._check_queue)
    
    def _start_bridge(self):
        global OMNI_BRIDGE
        if OMNI_BRIDGE is None:
            OMNI_BRIDGE = omni_bridge.OmniagentBridge()
            # Start bridge with callback
            OMNI_BRIDGE.start(self._on_bridge_output)
            
    def _on_bridge_output(self, char):
        """Callback from bridge thread, put char in queue"""
        self.msg_queue.put(char)
        
    def _check_queue(self):
        """Poll queue for messages and accumulate chunk"""
        try:
            chunk = ""
            while True:
                # Get everything available
                char = self.msg_queue.get_nowait()
                chunk += char
        except queue.Empty:
            if chunk:
                # Clean ANSI from the accumulated chunk
                clean_chunk = clean_ansi(chunk)
                if clean_chunk:
                    self._handle_bridge_message(clean_chunk)
        
        if self.running:
            self.root.after(50, self._check_queue)
            
    def _handle_bridge_message(self, text):
        """Update UI with specific text"""
        # Log (Raw text, mostly)
        self.log_window.log('Agent', text)
        
        # Update response panel
        # If panel is hidden, show it
        if not self.response_panel.winfo_viewable() and text.strip():
             self.response_panel.deiconify()
             
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, text)
        self.response_text.see(tk.END)
        self.response_text.config(state=tk.DISABLED)
        
        # Auto-hide timer reset
        if self.response_timer: self.root.after_cancel(self.response_timer)
        # self.response_timer = self.root.after(10000, self._hide_response)

    def _load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except: pass
        return {}

    def _load_assets(self):
        try:
            assets_dir = os.path.join(PROJECT_ROOT, 'assets')
            # Logo for response panel / taskbar
            logo_path = os.path.join(assets_dir, '32-icon.ico')
            if os.path.exists(logo_path):
                img = Image.open(logo_path).resize((20, 20), Image.Resampling.LANCZOS)
                self.assets['logo_small'] = ImageTk.PhotoImage(img)
                
                img_l = Image.open(logo_path).resize((28, 28), Image.Resampling.LANCZOS)
                self.assets['logo_med'] = ImageTk.PhotoImage(img_l)
        except Exception as e:
            print(f"Asset load error: {e}")

    def _create_taskbar(self):
        self.taskbar = tk.Toplevel(self.root)
        self.taskbar.overrideredirect(True)
        self.taskbar.attributes('-topmost', True)
        self.taskbar.attributes('-alpha', 0.95)
        self.taskbar.geometry(f"{self.screen_width}x{self.taskbar_height}+0+0")
        self.taskbar.configure(bg=self.colors['bg_glass'])
        
        hwnd = int(self.taskbar.winfo_id())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_TOOLWINDOW)
        
        main = tk.Frame(self.taskbar, bg=self.colors['bg_glass'])
        main.pack(fill=tk.BOTH, expand=True)
        
        gradient_line = tk.Frame(main, bg=self.colors['accent'], height=2)
        gradient_line.pack(side=tk.BOTTOM, fill=tk.X)
        
        content = tk.Frame(main, bg=self.colors['bg_glass'])
        content.pack(fill=tk.BOTH, expand=True)
        
        # LEFT
        left = tk.Frame(content, bg=self.colors['bg_glass'])
        left.pack(side=tk.LEFT, padx=16)
        
        if 'logo_small' in self.assets:
             # Added padding to prevent cut-off
             tk.Label(left, image=self.assets['logo_small'], bg=self.colors['bg_glass']).pack(side=tk.LEFT, pady=2)
        else:
             tk.Label(left, text="✦", font=('Segoe UI Symbol', 16),
                      fg=self.colors['accent'], bg=self.colors['bg_glass']).pack(side=tk.LEFT, pady=2)
        
        tk.Label(left, text="Horizon", font=self.font_header,
                 fg=self.colors['text'], bg=self.colors['bg_glass']).pack(side=tk.LEFT, padx=(4, 0))
        
        # CENTER-LEFT
        self.apps_frame = tk.Frame(content, bg=self.colors['bg_glass'])
        self.apps_frame.pack(side=tk.LEFT, padx=24)
        
        # CENTER
        self.status_frame = tk.Frame(content, bg=self.colors['bg_glass'])
        self.status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.status_container = tk.Frame(self.status_frame, bg=self.colors['bg_glass_light'], padx=12, pady=4)
        self.status_container.pack(expand=True)
        
        self.status_label = tk.Label(self.status_container, text="", font=self.font_body,
                                     fg=self.colors['text_muted'], bg=self.colors['bg_glass_light'])
        self.status_label.pack()
        
        # RIGHT
        right = tk.Frame(content, bg=self.colors['bg_glass'])
        right.pack(side=tk.RIGHT, padx=16)
        
        self.time_label = tk.Label(right, text="", font=self.font_time,
                                   fg=self.colors['text'], bg=self.colors['bg_glass'])
        self.time_label.pack(side=tk.RIGHT, padx=12)
        self._update_time()
        
        # Logs Button
        log_btn = tk.Label(right, text="📜", font=('Segoe UI Symbol', 14),
                           fg=self.colors['text_secondary'], bg=self.colors['bg_glass'], cursor='hand2')
        log_btn.pack(side=tk.RIGHT, padx=8)
        log_btn.bind('<Button-1>', lambda e: self.log_window.toggle())
        
        chat_btn = tk.Label(right, text="💬", font=('Segoe UI', 14),
                           fg=self.colors['text_secondary'], bg=self.colors['bg_glass'], cursor='hand2')
        chat_btn.pack(side=tk.RIGHT, padx=8)
        chat_btn.bind('<Button-1>', lambda e: self._switch_to_chat())
        
        # Custom Window Controls
        ctrls = self._create_custom_controls(right, self._exit)
        ctrls.pack(side=tk.RIGHT, padx=8)
    
    def _set_status(self, text):
        self.status_label.config(text=text, fg=self.colors['text_muted'])
    
    def _create_response_panel(self):
        self.response_panel = tk.Toplevel(self.root)
        self.response_panel.overrideredirect(True)
        self.response_panel.attributes('-topmost', True)
        self.response_panel.attributes('-alpha', 0.96)
        self.response_panel.withdraw()
        
        width, height = self.prompt_width, 200
        x = (self.screen_width - width) // 2
        y = self.screen_height - 72 - 20 - height - 16
        
        self.response_panel.geometry(f"{width}x{height}+{x}+{y}")
        self.response_panel.configure(bg=self.colors['bg_glass'])
        
        hwnd = int(self.response_panel.winfo_id())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_TOOLWINDOW)
        
        outer = tk.Frame(self.response_panel, bg=self.colors['border_glow'])
        outer.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        container = tk.Frame(outer, bg=self.colors['bg_glass_card'])
        container.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(container, bg=self.colors['bg_glass_card'])
        header.pack(fill=tk.X, padx=20, pady=(14, 8))
        
        if 'logo_small' in self.assets:
             tk.Label(header, image=self.assets['logo_small'], bg=self.colors['bg_glass_card']).pack(side=tk.LEFT)
        else:
             tk.Label(header, text="✦", font=('Segoe UI Symbol', 14),
                      fg=self.colors['accent_light'], bg=self.colors['bg_glass_card']).pack(side=tk.LEFT)
        
        tk.Label(header, text="Horizon Response", font=('Segoe UI', 11),
                fg=self.colors['text_secondary'], bg=self.colors['bg_glass_card']).pack(side=tk.LEFT, padx=(8, 0))
        
        # Custom Controls
        ctrls = self._create_custom_controls(header, self._hide_response)
        ctrls.pack(side=tk.RIGHT)
        
        content = tk.Frame(container, bg=self.colors['bg_glass_light'])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 14))
        
        self.response_text = tk.Text(content, font=('Segoe UI', 12),
                                     fg=self.colors['text'], bg=self.colors['bg_glass_light'],
                                     relief=tk.FLAT, wrap=tk.WORD, padx=14, pady=12)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        self.response_text.config(state=tk.DISABLED)
    
    def _show_response(self, text):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete('1.0', tk.END)
        self.response_text.insert('end', text)
        self.response_text.config(state=tk.DISABLED)
        
        if not self.response_panel.winfo_viewable():
             self._animate_fade_in(self.response_panel, target_alpha=0.96)
        
        if self.response_timer: self.root.after_cancel(self.response_timer)
        self.response_timer = self.root.after(5000, self._hide_response)
    
    def _hide_response(self):
        self.response_panel.withdraw()
        if self.response_timer:
            self.root.after_cancel(self.response_timer)
            self.response_timer = None
    
    def _create_prompt(self):
        self.prompt = tk.Toplevel(self.root)
        self.prompt.overrideredirect(True)
        self.prompt.attributes('-topmost', True)
        self.prompt.attributes('-alpha', 0.96)
        
        width = self.prompt_width
        height = 68
        x = (self.screen_width - width) // 2
        y = self.screen_height - height - 30
        
        self.prompt.geometry(f"{width}x{height}+{x}+{y}")
        self.prompt.configure(bg='#000000') 
        self.prompt.wm_attributes("-transparentcolor", "#000000")
        
        self.canvas = tk.Canvas(self.prompt, width=width, height=height, 
                               bg='#000000', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        r = 34
        self.canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=self.colors['bg_glass_card'], outline=self.colors['border_glow'], width=1)
        self.canvas.create_arc(width-2*r, 0, width, 2*r, start=0, extent=90, fill=self.colors['bg_glass_card'], outline=self.colors['border_glow'], width=1)
        self.canvas.create_arc(width-2*r, height-2*r, width, height, start=270, extent=90, fill=self.colors['bg_glass_card'], outline=self.colors['border_glow'], width=1)
        self.canvas.create_arc(0, height-2*r, 2*r, height, start=180, extent=90, fill=self.colors['bg_glass_card'], outline=self.colors['border_glow'], width=1)
        
        self.canvas.create_rectangle(r, 0, width-r, height+1, fill=self.colors['bg_glass_card'], outline="")
        self.canvas.create_rectangle(0, r, width+1, height-r, fill=self.colors['bg_glass_card'], outline="")
        
        self.canvas.create_line(r, 0, width-r, 0, fill=self.colors['border_glow'])
        self.canvas.create_line(r, height, width-r, height, fill=self.colors['border_glow'])
        
        container = tk.Frame(self.prompt, bg=self.colors['bg_glass_card'])
        container.place(x=r, y=8, width=width-2*r, height=height-16)
        
        if 'logo_med' in self.assets:
             tk.Label(container, image=self.assets['logo_med'], bg=self.colors['bg_glass_card']).pack(side=tk.LEFT, padx=(0, 10))
        else:
             tk.Label(container, text="✦", font=('Segoe UI Symbol', 20),
                      fg=self.colors['accent'], bg=self.colors['bg_glass_card']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(container, textvariable=self.input_var, font=('Segoe UI Variable Display', 14),
                             fg=self.colors['text'], bg=self.colors['bg_glass_card'],
                             insertbackground=self.colors['accent'], relief=tk.FLAT)
        self.entry.insert(0, "Ask anything... (@settings)")
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry.bind('<FocusIn>', self._on_focus)
        self.entry.bind('<FocusOut>', self._on_blur)
        self.entry.bind('<Return>', self._on_submit)
        
        btn_cv = tk.Canvas(container, width=40, height=40, bg=self.colors['bg_glass_card'], highlightthickness=0)
        btn_cv.pack(side=tk.RIGHT, padx=(10, 0))
        btn_cv.create_oval(2, 2, 38, 38, fill=self.colors['accent'], outline="")
        btn_cv.create_text(20, 20, text="→", fill='white', font=('Segoe UI', 14, 'bold'))
        btn_cv.bind('<Button-1>', self._on_submit)
    
    def _on_focus(self, e):
        if self.input_var.get() == "Ask anything... (@settings)":
            self.input_var.set("")
            self.entry.config(fg=self.colors['text'])
    
    def _on_blur(self, e):
        if not self.input_var.get():
            self.input_var.set("Ask anything... (@settings)")
            self.entry.config(fg=self.colors['text_muted'])
            
    def _on_submit(self, e=None):
        query = self.input_var.get().strip()
        if not query or query == "Ask anything... (@settings)": return
        
        if query.lower() == "@settings":
            self.input_var.set("")
            self._open_settings()
            return
            
        if query.lower() == "@logs":
            self.input_var.set("")
            self.log_window.toggle()
            return
            
        if query.lower() == "cls" or query.lower() == "clear":
             self.response_text.config(state=tk.NORMAL)
             self.response_text.delete('1.0', tk.END)
             self.response_text.config(state=tk.DISABLED)
             self.input_var.set("")
             return

        self.input_var.set("")
        self._set_status("➤ Sending...")
        
        # Log User Query
        self.log_window.log('User', query + "\n")
        
        # Send to bridge (Stream)
        global OMNI_BRIDGE
        if OMNI_BRIDGE:
            OMNI_BRIDGE.write(query)
            # If response panel is hidden, show it so user sees result
            self.response_panel.deiconify()
             
        self.taskbar.after(500, lambda: self._set_status(""))

    def _reserve_screen_space(self):
        try:
            work_area = wintypes.RECT()
            work_area.left = 0
            work_area.top = self.taskbar_height
            work_area.right = self.screen_width
            work_area.bottom = self.screen_height
            user32.SystemParametersInfoW(0x002F, 0, byref(work_area), 0)
        except: pass
    
    def _restore_screen_space(self):
        try:
            work_area = wintypes.RECT()
            work_area.left = 0
            work_area.top = 0
            work_area.right = self.screen_width
            work_area.bottom = self.screen_height
            user32.SystemParametersInfoW(0x002F, 0, byref(work_area), 0)
        except: pass
    
    def _update_time(self):
        from datetime import datetime
        self.time_label.config(text=datetime.now().strftime("%H:%M"))
        self.taskbar.after(1000, self._update_time)
    
    def _get_exe_icon(self, exe_path, size=24):
        if exe_path in self.exe_icon_cache: return self.exe_icon_cache[exe_path]
        try:
            large, small = win32gui.ExtractIconEx(exe_path, 0, 10)
            if large:
                hicon = large[0]
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, size, size)
                hdc_mem = hdc.CreateCompatibleDC()
                hdc_mem.SelectObject(hbmp)
                hdc_mem.FillSolidRect((0, 0, size, size), 0x000000)
                win32gui.DrawIconEx(hdc_mem.GetSafeHdc(), 0, 0, hicon, size, size, 0, None, win32con.DI_NORMAL)
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer('RGBA', (size, size), bmpstr, 'raw', 'BGRA', 0, 1)
                hdc_mem.DeleteDC()
                win32gui.ReleaseDC(0, hdc.GetSafeHdc())
                for h in large: win32gui.DestroyIcon(h)
                for h in small: win32gui.DestroyIcon(h)
                self.exe_icon_cache[exe_path] = img
                return img
        except: pass
        return None
    
    def _get_window_exe(self, hwnd):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).exe()
        except: return None
    
    def _start_window_tracking(self):
        def track():
            while self.running:
                self._update_apps()
                time.sleep(1)
        threading.Thread(target=track, daemon=True).start()
    
    def _update_apps(self):
        apps = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and len(title) > 0 and 'Horizon' not in title:
                    skip = ['', 'Program Manager', 'Windows Input Experience', 'Settings']
                    if title not in skip:
                        apps.append((hwnd, title, self._get_window_exe(hwnd)))
            return True
        try: win32gui.EnumWindows(callback, None)
        except: pass
        self.taskbar.after(0, lambda: self._refresh_icons(apps[:10]))
    
    def _refresh_icons(self, apps):
        for w in self.apps_frame.winfo_children(): w.destroy()
        for hwnd, title, exe in apps:
            btn_frame = tk.Frame(self.apps_frame, bg=self.colors['bg_glass'])
            btn_frame.pack(side=tk.LEFT, padx=2)
            icon_img = self._get_exe_icon(exe) if exe else None
            if icon_img is None:
                icon_img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
                draw = ImageDraw.Draw(icon_img)
                draw.rounded_rectangle([(2, 2), (22, 22)], radius=6, fill=self.colors['accent'])
            else:
                icon_img = icon_img.resize((24, 24), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(icon_img)
            self.icon_cache[hwnd] = photo
            btn = tk.Label(btn_frame, image=photo, bg=self.colors['bg_glass'], cursor='hand2')
            btn.image = photo
            btn.pack(padx=4, pady=9)
            btn.bind('<Button-1>', lambda e, h=hwnd: self._activate_window(h))
            btn.bind('<Enter>', lambda e, f=btn_frame: f.config(bg=self.colors['bg_hover']))
            btn.bind('<Leave>', lambda e, f=btn_frame: f.config(bg=self.colors['bg_glass']))
            
    def _activate_window(self, hwnd):
        try:
            if win32gui.IsIconic(hwnd): win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        except: pass
    
    def _switch_to_chat(self):
        chat_script = os.path.join(os.path.dirname(__file__), 'chat_window.py')
        if os.path.exists(chat_script):
            subprocess.Popen(['python', chat_script], creationflags=subprocess.CREATE_NO_WINDOW)
        self._exit()
    
    def _animate_fade_in(self, window, target_alpha=1.0, steps=10):
        """Smooth fade in animation"""
        try:
            current = 0.0
            window.attributes('-alpha', current)
            window.deiconify()
            
            def step():
                nonlocal current
                current += target_alpha / steps
                if current >= target_alpha:
                    window.attributes('-alpha', target_alpha)
                else:
                    window.attributes('-alpha', current)
                    window.after(16, step)
            step()
        except: pass
        
    def _open_settings(self):
        try:
            settings_script = os.path.join(os.path.dirname(__file__), 'settings_window.py')
            if os.path.exists(settings_script):
                subprocess.Popen(['python', settings_script], creationflags=subprocess.CREATE_NO_WINDOW)
                self._set_status("⚙ Settings opened")
        except: pass

    def _create_custom_controls(self, parent, command_close):
        style = self.tm.get_window_style()
        frame = tk.Frame(parent, bg=parent['bg'])
        
        if style == 'macos':
            # Traffic Lights
            btn_close = tk.Canvas(frame, width=14, height=14, bg=parent['bg'], highlightthickness=0, cursor='hand2')
            btn_close.create_oval(1, 1, 13, 13, fill='#ff5f56', outline='#e0443e')
            btn_close.bind('<Button-1>', lambda e: command_close())
            btn_close.pack(side=tk.LEFT, padx=3)
            
            btn_min = tk.Canvas(frame, width=14, height=14, bg=parent['bg'], highlightthickness=0)
            btn_min.create_oval(1, 1, 13, 13, fill='#ffbd2e', outline='#d89e24')
            btn_min.pack(side=tk.LEFT, padx=3)
            
            btn_max = tk.Canvas(frame, width=14, height=14, bg=parent['bg'], highlightthickness=0)
            btn_max.create_oval(1, 1, 13, 13, fill='#27c93f', outline='#1aab29')
            btn_max.pack(side=tk.LEFT, padx=3)
            
        elif style == 'sleek':
            # Dots
            btn_close = tk.Label(frame, text="●", font=('Arial', 14), fg='#9ca3af', bg=parent['bg'], cursor='hand2')
            btn_close.bind('<Enter>', lambda e: e.widget.config(fg=self.colors['accent']))
            btn_close.bind('<Leave>', lambda e: e.widget.config(fg='#9ca3af'))
            btn_close.bind('<Button-1>', lambda e: command_close())
            btn_close.pack(side=tk.LEFT, padx=2)
            
            tk.Label(frame, text="●", font=('Arial', 14), fg='#9ca3af', bg=parent['bg']).pack(side=tk.LEFT, padx=2)
            
        else: # Default or Minimal
            sym = "✕" if style == 'default' else "—"
            btn = tk.Label(frame, text=sym, font=('Segoe UI', 11), fg=self.colors['text_muted'], bg=parent['bg'], cursor='hand2')
            btn.bind('<Button-1>', lambda e: command_close())
            btn.pack()
            
        return frame

    def _exit(self):
        self.running = False
        self._restore_screen_space()
        taskbar = user32.FindWindowW("Shell_TrayWnd", None)
        if taskbar: user32.ShowWindow(taskbar, 5)
        self.response_panel.destroy()
        self.prompt.destroy()
        self.taskbar.destroy()
        self.root.destroy()
        if OMNI_BRIDGE: OMNI_BRIDGE.stop()

    def run(self):
        # Updated banner for confirmation
        print("\n✨ Horizon Giga UI v9 (Premium)")
        print("   ✓ AI Bridge Active")
        print("   ✓ Click ⊞ to exit\n")
        self.root.mainloop()

def main():
    taskbar = user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar: user32.ShowWindow(taskbar, 0)
    GigaUI().run()

if __name__ == '__main__':
    main()
