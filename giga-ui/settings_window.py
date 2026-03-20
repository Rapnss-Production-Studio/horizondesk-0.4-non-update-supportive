import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
import os
import sys
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import theme_manager
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    import theme_manager

class SettingsWindow:
    """
    Aesthetic Settings Window
    - White Background, Black Text
    - Clean Tabs
    - Visual Previews
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Settings")
        self.root.geometry("900x650") 
        self.root.configure(bg="#ffffff")
        
        self.tm = theme_manager.ThemeManager()
        self.config = self.tm.config.get('theme', {})
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure Notebook (Tabs)
        self.style.configure("TNotebook", background="#ffffff", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#f3f4f6", foreground="#4b5563", 
                           padding=[20, 10], font=("Segoe UI Variable Display", 10))
        self.style.map("TNotebook.Tab", background=[("selected", "#ffffff")], 
                     foreground=[("selected", "#111827")])
        
        # Font Configuration
        self.header_font = ("Segoe UI Variable Display", 18, "bold")
        self.sub_font = ("Segoe UI Variable Display", 12, "bold")
        self.body_font = ("Segoe UI Variable Display", 10)
        
        self._build_ui()
        self._load_current_values()
        
    def _build_ui(self):
        # Sidebar or Topbar? Let's use Topbar Notebook for simplicity and elegance.
        
        header = tk.Frame(self.root, bg="#ffffff", height=60)
        header.pack(fill=tk.X, padx=40, pady=20)
        
        tk.Label(header, text="Settings", font=("Segoe UI Variable Display", 24, "bold"), 
                 bg="#ffffff", fg="#000000").pack(side=tk.LEFT)
        
        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))
        
        self.tab_wall = tk.Frame(self.notebook, bg="#ffffff")
        self.tab_appearance = tk.Frame(self.notebook, bg="#ffffff")
        self.tab_type = tk.Frame(self.notebook, bg="#ffffff")
        self.tab_window = tk.Frame(self.notebook, bg="#ffffff")
        
        self.notebook.add(self.tab_wall, text="Wallpaper")
        self.notebook.add(self.tab_appearance, text="Appearance")
        self.notebook.add(self.tab_type, text="Typography")
        self.notebook.add(self.tab_window, text="Window Style")
        
        self._build_wallpaper_tab()
        self._build_appearance_tab()
        self._build_typography_tab()
        self._build_window_style_tab()
        
    def _build_wallpaper_tab(self):
        # Grid of wallpapers
        container = tk.Frame(self.tab_wall, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(container, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.wall_frame = tk.Frame(canvas, bg="#ffffff")
        
        self.wall_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.wall_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load wallpapers
        threading.Thread(target=self._load_wallpapers, daemon=True).start()
        
    def _load_wallpapers(self):
        wallpaper_dir = os.path.join(PROJECT_ROOT, "wallpaper")
        if not os.path.exists(wallpaper_dir): return
        
        row, col = 0, 0
        max_cols = 3
        
        files = [f for f in os.listdir(wallpaper_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for f in files:
            path = os.path.join(wallpaper_dir, f)
            try:
                img = Image.open(path)
                img.thumbnail((200, 150))
                photo = ImageTk.PhotoImage(img)
                
                frame = tk.Frame(self.wall_frame, bg="#ffffff", padx=10, pady=10)
                frame.grid(row=row, column=col, sticky="n")
                
                label = tk.Label(frame, image=photo, bg="#ffffff", cursor="hand2")
                label.image = photo
                label.pack()
                label.bind("<Button-1>", lambda e, p=path: self._apply_wallpaper(p))
                
                tk.Label(frame, text=f, font=self.body_font, bg="#ffffff", fg="#4b5563").pack(pady=5)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except: pass

    def _apply_wallpaper(self, path):
        self.tm.apply_theme(path)
        tk.messagebox.showinfo("Applied", "Wallpaper and theme applied successfully.")

    def _build_appearance_tab(self):
        frame = tk.Frame(self.tab_appearance, bg="#ffffff", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Color Pickers
        tk.Label(frame, text="Custom Colors", font=self.sub_font, bg="#ffffff", fg="#000000").pack(anchor="w", pady=(0, 10))
        
        colors = [
            ("Accent Color", "accent"),
            ("Glass Background", "bg_glass"),
            ("Card Background", "bg_glass_card"),
            ("Primary Text", "text")
        ]
        
        for label, key in colors:
            row = tk.Frame(frame, bg="#ffffff")
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=label, font=self.body_font, bg="#ffffff", width=20, anchor="w").pack(side=tk.LEFT)
            btn = tk.Button(row, text="Pick Color", command=lambda k=key: self._pick_color(k))
            btn.pack(side=tk.LEFT)
            
        # Transparency Slider
        tk.Label(frame, text="Transparency", font=self.sub_font, bg="#ffffff", fg="#000000").pack(anchor="w", pady=(20, 10))
        self.trans_scale = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, 
                                  bg="#ffffff", highlightthickness=0, command=self._save_transparency)
        self.trans_scale.set(self.config.get('transparency', 0.95))
        self.trans_scale.pack(fill=tk.X, padx=20)

    def _pick_color(self, key):
        color = colorchooser.askcolor(title=f"Choose {key}")[1]
        if color:
            self.tm.save_custom_color(key, color)

    def _save_transparency(self, val):
        # We can implement a debounce here if needed, but for now direct save
        pass 

    def _build_typography_tab(self):
        frame = tk.Frame(self.tab_type, bg="#ffffff", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Font Family", font=self.sub_font, bg="#ffffff", fg="#000000").pack(anchor="w")
        
        # Scrolled List of Fonts
        fonts_frame = tk.Frame(frame)
        fonts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(fonts_frame)
        fonts_list = tk.Listbox(fonts_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 12), 
                              selectmode=tk.SINGLE, borderwidth=0, highlightthickness=1)
        scrollbar.config(command=fonts_list.yview)
        
        fonts_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate fonts (basic set + system)
        system_fonts = sorted(list(tk.font.families()))
        for f in system_fonts:
            if not f.startswith("@"):
                fonts_list.insert(tk.END, f)
                
        fonts_list.bind('<<ListboxSelect>>', lambda e: self._on_font_select(fonts_list))
        
        # Weight
        tk.Label(frame, text="Font Weight", font=self.sub_font, bg="#ffffff", fg="#000000").pack(anchor="w", pady=(20, 5))
        self.weight_var = tk.StringVar(value=self.config.get('font_weight', 'light'))
        
        modes = [("Light / Thin", "light"), ("Normal", "normal"), ("Bold", "bold")]
        for text, val in modes:
            tk.Radiobutton(frame, text=text, variable=self.weight_var, value=val, 
                         bg="#ffffff", command=self._save_font_config).pack(anchor="w")

    def _on_font_select(self, listbox):
        selection = listbox.curselection()
        if selection:
            font = listbox.get(selection[0])
            self.tm.save_font_settings(font, self.weight_var.get())

    def _save_font_config(self):
        # Current font is hard to pull from listbox if not selected, so we assume separate save or store current
        # For simplicity, we just save weight here if we knew the family.
        # Let's rely on listbox selection mainly.
        pass

    def _build_window_style_tab(self):
        frame = tk.Frame(self.tab_window, bg="#ffffff", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Window Control Style", font=self.sub_font, bg="#ffffff", fg="#000000").pack(anchor="w", pady=(0, 20))
        
        styles = [
            ("macOS Style (Traffic Lights)", "macos"),
            ("Windows Default (Box)", "default"),
            ("Minimal (Lines)", "minimal"),
            ("Sleek (Dots)", "sleek")
        ]
        
        self.style_var = tk.StringVar(value=self.config.get('window_style', 'macos'))
        
        for text, val in styles:
            row = tk.Frame(frame, bg="#ffffff", pady=10)
            row.pack(fill=tk.X)
            
            rb = tk.Radiobutton(row, text=text, variable=self.style_var, value=val, 
                              bg="#ffffff", font=self.body_font, command=lambda v=val: self.tm.save_window_style(v))
            rb.pack(side=tk.LEFT)
            
            # Preview (Simulated)
            preview = tk.Canvas(row, width=60, height=20, bg="#e5e5e5", highlightthickness=0)
            preview.pack(side=tk.RIGHT)
            self._draw_preview(preview, val)

    def _draw_preview(self, canvas, style):
        # Draw simulated controls
        if style == 'macos':
            canvas.create_oval(5, 5, 15, 15, fill="#ff5f56", outline="")
            canvas.create_oval(20, 5, 30, 15, fill="#ffbd2e", outline="")
            canvas.create_oval(35, 5, 45, 15, fill="#27c93f", outline="")
        elif style == 'default':
            canvas.create_text(30, 10, text="—  □  ✕", fill="#000000")
        elif style == 'minimal':
            canvas.create_line(10, 10, 20, 10, fill="#000000", width=2)
            canvas.create_line(40, 5, 50, 15, fill="#000000", width=2)
            canvas.create_line(40, 15, 50, 5, fill="#000000", width=2)
        elif style == 'sleek':
            canvas.create_oval(10, 7, 16, 13, fill="#9ca3af", outline="")
            canvas.create_oval(25, 7, 31, 13, fill="#9ca3af", outline="")
            canvas.create_oval(40, 7, 46, 13, fill="#9ca3af", outline="")

    def _load_current_values(self):
        # Additional logic to set listbox selection etc.
        pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    SettingsWindow().run()
