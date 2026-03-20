
"""
Horizon Chat Window - Compact 9:16 Sidebar UI
- 300px width x 533px height (9:16 ratio)
- Always on top, right side of screen
- Modern glassmorphism design
- Omniagent Integration
- Dynamic Theming
"""

import tkinter as tk
from tkinter import ttk
import ctypes
from ctypes import wintypes
import os
import json
import threading
import time
from datetime import datetime
from PIL import Image, ImageTk

# Project Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from giga_ui import omni_bridge
    from giga_ui import theme_manager
except ImportError:
    # Fallback if running directly from folder
    import omni_bridge
    import theme_manager

user32 = ctypes.windll.user32

# Config paths
HORIZON_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'HorizonDesk')
CONFIG_FILE = os.path.join(HORIZON_DIR, 'config.json')

class HorizonChatWindow:
    """Compact 9:16 Chat Window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Window size: 9:16 ratio, 300px width
        self.width = 360 # Increased width slightly
        self.height = 640
        
        # Position: right side of screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width - self.width - 20
        self.y = (screen_height - self.height) // 2
        
        # Theme & Bridge
        self.tm = theme_manager.ThemeManager()
        self.bridge = omni_bridge.OmniagentBridge()
        
        # Load Theme Colors & Tweaks
        self._load_colors()
        
        # Load Assets
        self.assets = {}
        self._load_assets()
        
        # Messages
        self.messages = []
        
        self._create_window()
        self._build_ui()
        
    def _load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except: pass
        return {}

    def _load_colors(self):
        # Force Light Theme
        palette = self.tm.get_theme_palette('light')
        self.colors = {
            'bg': palette['bg_glass'],
            'panel': palette['bg_glass_light'], # Use light gray for panel
            'input_bg': palette['input_bg'],
            'accent': palette['accent'],
            'accent_dim': palette['accent_light'],
            'text': palette['text'],
            'text_muted': palette['text_muted'],
            'border': palette['border'],
            'user_bubble': palette['user_bubble'],
            'ai_bubble': palette['ai_bubble']
        }
        
    def _load_assets(self):
        assets_dir = os.path.join(PROJECT_ROOT, 'assets')
        try:
            # 32px icon for header
            logo_path = os.path.join(assets_dir, '32-icon.ico')
            if os.path.exists(logo_path):
                img = Image.open(logo_path).resize((20, 20), Image.Resampling.LANCZOS)
                self.assets['logo'] = ImageTk.PhotoImage(img)
            
            # 16px icon for window
            icon_path = os.path.join(assets_dir, '16-icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                
        except Exception as e:
            print(f"Asset load error: {e}")
    
    def _create_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Horizon")
        self.window.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        self.window.configure(bg=self.colors['bg'])
        self.window.attributes('-topmost', True)
        self.window.resizable(False, False)
        self.window.overrideredirect(True)
        
        # Border frame
        self.border_frame = tk.Frame(self.window, bg=self.colors['accent'], padx=1, pady=1)
        self.border_frame.pack(fill=tk.BOTH, expand=True)
        
        self.inner_window = tk.Frame(self.border_frame, bg=self.colors['bg'])
        self.inner_window.pack(fill=tk.BOTH, expand=True)
        
        self._create_title_bar()
    
    def _create_title_bar(self):
        self.title_bar = tk.Frame(self.inner_window, bg=self.colors['panel'], height=40)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # Logo and title
        left = tk.Frame(self.title_bar, bg=self.colors['panel'])
        left.pack(side=tk.LEFT, padx=12, fill=tk.Y)
        
        if 'logo' in self.assets:
            tk.Label(left, image=self.assets['logo'], bg=self.colors['panel']).pack(side=tk.LEFT, pady=8)
        else:
            tk.Label(left, text="✦", font=('Segoe UI Symbol', 14),
                    fg=self.colors['accent'], bg=self.colors['panel']).pack(side=tk.LEFT, pady=8)
            
        font_header = self.tm.get_font(11, 'bold')
        tk.Label(left, text="Horizon", font=font_header,
                fg=self.colors['text'], bg=self.colors['panel']).pack(side=tk.LEFT, padx=8)
        
        # Controls
        controls = tk.Frame(self.title_bar, bg=self.colors['panel'])
        controls.pack(side=tk.RIGHT, padx=8)
        
        # Custom Controls
        ctrls = self._create_custom_controls(self.title_bar, self._close)
        ctrls.pack(side=tk.RIGHT, padx=8)
        
        # Dragging
        self.title_bar.bind('<Button-1>', self._start_drag)
        self.title_bar.bind('<B1-Motion>', self._on_drag)
    
    def _start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
    
    def _on_drag(self, event):
        x = self.window.winfo_x() + event.x - self.drag_x
        y = self.window.winfo_y() + event.y - self.drag_y
        self.window.geometry(f"+{x}+{y}")
    
    def _build_ui(self):
        # Messages area
        self.messages_frame = tk.Frame(self.inner_window, bg=self.colors['bg'])
        self.messages_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.canvas = tk.Canvas(self.messages_frame, bg=self.colors['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.messages_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.messages_container = tk.Frame(self.canvas, bg=self.colors['bg'])
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.messages_container, anchor='nw', width=self.width - 20)
        
        self.messages_container.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        self._add_message("Hello! I'm Horizon. How can I help?", is_user=False)
        
        # Input area
        input_frame = tk.Frame(self.inner_window, bg=self.colors['panel'])
        input_frame.pack(fill=tk.X, padx=0, pady=0)
        
        input_inner = tk.Frame(input_frame, bg=self.colors['input_bg'], padx=8, pady=8)
        input_inner.pack(fill=tk.X, padx=12, pady=12)
        
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(input_inner, textvariable=self.input_var,
                             font=('Segoe UI Variable Display', 11), fg=self.colors['text'],
                             bg=self.colors['input_bg'], insertbackground=self.colors['accent'],
                             relief=tk.FLAT, border=0)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<Return>', self._on_send)
        self.entry.focus_set()
        
        send_btn = tk.Label(input_inner, text="↑", font=('Segoe UI', 14, 'bold'),
                           fg=self.colors['accent'], bg=self.colors['input_bg'], cursor='hand2')
        send_btn.pack(side=tk.RIGHT, padx=4)
        send_btn.bind('<Button-1>', self._on_send)
    
    def _add_message(self, text, is_user=False):
        msg_frame = tk.Frame(self.messages_container, bg=self.colors['bg'])
        msg_frame.pack(fill=tk.X, pady=4, padx=8)
        
        bubble_bg = self.colors['user_bubble'] if is_user else self.colors['ai_bubble']
        # User bubble text usually accent for light theme, or dark gray
        fg_col = self.colors['text'] if not is_user else '#1e1b4b' # Dark indigo for user bubble
        anchor = 'e' if is_user else 'w'
        
        bubble = tk.Frame(msg_frame, bg=bubble_bg)
        bubble.pack(anchor=anchor, padx=(40, 0) if is_user else (0, 40))
        
        tk.Label(bubble, text=text, font=('Segoe UI Variable Display', 10),
                fg=fg_col, bg=bubble_bg, wraplength=220, justify=tk.LEFT, padx=10, pady=8).pack()
        
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def _on_send(self, event=None):
        text = self.input_var.get().strip()
        if not text: return
        
        self.input_var.set("")
        self._add_message(text, is_user=True)
        
        def process():
            response = self.bridge.send_query(text)
            self.root.after(0, lambda: self._add_message(response, is_user=False))
        
        threading.Thread(target=process, daemon=True).start()

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
    
    def _close(self):
        self.bridge.stop()
        self.window.destroy()
        self.root.destroy()
    
    def run(self):
        self.window.deiconify()
        self.root.mainloop()

if __name__ == '__main__':
    chat = HorizonChatWindow()
    chat.run()
