from pynput import keyboard, mouse
import threading
import time
from colorama import Fore
from core.overlay import OverlaySystem

class InputManager:
    def __init__(self):
        self.suppress = False
        self.keyboard_listener = None
        self.mouse_listener = None
        self.exit_requested = False
        
        # Overlay
        self.overlay = OverlaySystem()
        
        # State for Alt+F7 tracking
        self.alt_pressed = False
    
    def on_press(self, key):
        # Always check for exit combo, even if suppressing
        try:
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.alt_pressed = True
            
            if self.alt_pressed and key == keyboard.Key.f7:
                print(Fore.RED + "\n[InputManager] EMERGENCY EXIT (Alt+F7) DETECTED! Unblocking...")
                self.stop_blocking()
                self.exit_requested = True
                return False # Stop listener
        except AttributeError:
            pass
            
        return not self.suppress # If suppress is True, return False (which stops listener? No, return False stops listener. Return None/True continues)
        # Wait, pynput suppress works by passing suppress=True to constructor.
        # But we want conditional suppression? 
        # Actually pynput win32 implementation with suppress=True blocks ALL events.
        # We cannot conditionally unblock specific keys easily in pynput without low level hooks.
        # However, pynput listeners run in a separate thread.
        
    def start_blocking(self):
        """
        Starts blocking all input.
        """
        self.suppress = True
        self.exit_requested = False
        
        # We launch listeners with suppress=True. 
        # PROBLEM: If we use suppress=True, we might not get the callback for Ctrl+Z on some systems,
        # OR we get it but can't pass it through.
        # On Windows, pynput suppress=True prevents the event from propagating to other apps.
        # Our on_press IS called.
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press, 
            on_release=self.on_release,
            suppress=False # Do NOT block input
        )
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click, 
            on_move=self.on_move, 
            on_scroll=self.on_scroll,
            suppress=False # Do NOT block input
        )
        
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        # Start Visual Feedback
        try:
            self.overlay.start()
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Overlay failed to start: {e}")
            
        print(Fore.GREEN + " [MONITOR] Agent Active. Overlay enabled. Press Alt+F7 to stop.")

    def stop_blocking(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        # Stop Visual Feedback
        self.overlay.stop()
            
        self.suppress = False
        print(Fore.GREEN + " [UNLOCKED] Input restored.")

    def on_release(self, key):
        if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            self.alt_pressed = False
        return not self.suppress # If suppress is True, this probably doesn't matter for propagation if initialized with suppress=True
            
    # Mouse callbacks (suppress all)
    def on_move(self, x, y): pass
    def on_click(self, x, y, button, pressed): pass
    def on_scroll(self, x, y, dx, dy): pass

    def temporarily_unlock_for_action(self, func, *args, **kwargs):
        """
        Pauses blocking, executes a function (like a click), then resumes.
        """
        was_blocking = self.suppress
        if was_blocking:
            self.stop_blocking()
            time.sleep(0.1) # Wait for unhook
        
        try:
            return func(*args, **kwargs)
        finally:
            if was_blocking and not self.exit_requested:
                self.start_blocking()

    def update_status(self, text, details=""):
        try:
            self.overlay.update_text(text, details)
        except: pass
