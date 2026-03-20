import tkinter as tk
import threading

class OverlaySystem:
    def __init__(self):
        self.root = None
        self.thread = None
        self.should_be_visible = False
        self.status_text = "OmniAgent Active"
        self.sub_text = "Waiting for task..."

    def _run_overlay(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True) # No title bar
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.9) # Slightly transparent
        self.root.wm_attributes("-disabled", True) # Click-through (mostly) or just ignored

        # Minimal Note Box Design
        # Position: Top Center or Bottom Right? User said "Note box will come... show indicator".
        # Let's put it Top Center for visibility.
        screen_width = self.root.winfo_screenwidth()
        width = 400
        height = 80
        x_pos = (screen_width // 2) - (width // 2)
        y_pos = 20 # 20px from top
        
        self.root.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        self.root.configure(bg="#212121")

        # Frame for styling
        frame = tk.Frame(self.root, bg="#212121", highlightbackground="#00BCD4", highlightthickness=2)
        frame.pack(fill="both", expand=True)

        # Label
        lbl_title = tk.Label(frame, text="OmniAgent Active", font=("Segoe UI", 12, "bold"), fg="#00BCD4", bg="#212121")
        lbl_title.pack(pady=(10, 0))
        
        lbl_desc = tk.Label(frame, text="Monitoring...", font=("Segoe UI", 10), fg="#B0BEC5", bg="#212121")
        lbl_desc.pack(pady=(0, 10))

        def update_state():
            # Update Text if changed
            if hasattr(self, 'status_text') and self.status_text:
                lbl_title.config(text=self.status_text)
            
            if hasattr(self, 'sub_text') and self.sub_text:
                lbl_desc.config(text=self.sub_text)

            if self.should_be_visible:
                if self.root.state() == 'withdrawn':
                    self.root.deiconify()
                    self.root.lift()
            else:
                if self.root.state() != 'withdrawn':
                    self.root.withdraw()
            
            # Check every 100ms
            self.root.after(100, update_state)
            if self.should_be_visible:
                if self.root.state() == 'withdrawn':
                    self.root.deiconify()
                    self.root.lift()
            else:
                if self.root.state() != 'withdrawn':
                    self.root.withdraw()
            
            # Check every 100ms
            self.root.after(100, update_state)

        if not self.should_be_visible:
            self.root.withdraw()
            
        update_state()
        self.root.mainloop()

    def start(self):
        self.should_be_visible = True
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run_overlay, daemon=True)
            self.thread.start()

    def stop(self):
        self.should_be_visible = False

    def update_text(self, title, subtitle):
        self.status_text = title
        self.sub_text = subtitle
