import pyautogui
import pyttsx3
import threading
from core.tools import BaseTool

class MouseDragTool(BaseTool):
    def __init__(self):
        super().__init__("MouseDrag", "Drags the mouse from current pos to (x, y) or between two points. Input: 'from_x', 'from_y' (optional), 'to_x', 'to_y'.")

    def execute(self, to_x=None, to_y=None, from_x=None, from_y=None, payload=None):
        try:
            if payload and isinstance(payload, dict):
                to_x = payload.get('to_x')
                to_y = payload.get('to_y')
                from_x = payload.get('from_x')
                from_y = payload.get('from_y')
            elif payload and not isinstance(payload, dict):
                return f"Error: Input payload must be a JSON dictionary with keys 'to_x', 'to_y'. Received: {type(payload)}"
            
            if to_x is None or to_y is None:
                return "Error: Destination coordinates (to_x, to_y) are required."
            
            to_x, to_y = int(to_x), int(to_y)
            
            if from_x is not None and from_y is not None:
                pyautogui.moveTo(int(from_x), int(from_y))
            
            # Drag with a small duration for smoothness
            pyautogui.dragTo(to_x, to_y, duration=0.2, button='left')
            return f"Dragged to {to_x}, {to_y}"
        except Exception as e:
            return f"Error dragging: {e}"

class MouseScrollTool(BaseTool):
    def __init__(self):
        super().__init__("Scroll", "Scrolls the screen up or down. Input: 'clicks' (positive=up, negative=down).")

    def execute(self, clicks=None, payload=None):
        if payload and isinstance(payload, dict):
             clicks = payload.get('clicks')
        elif payload and not isinstance(payload, dict):
             # Maybe they passed the number directly? 
             try:
                 clicks = int(payload)
             except:
                 return f"Error: Input must be JSON {{'clicks': N}} or an integer. Received: {payload}"
        
        if clicks is None:
            return "Error: Number of clicks required."
            
        try:
            val = int(clicks)
            pyautogui.scroll(val)
            return f"Scrolled {val} units."
        except Exception as e:
            return f"Error scrolling: {e}"

class SpeakTool(BaseTool):
    def __init__(self):
        super().__init__("Speak", "Uses TTS to speak text out loud. Input: 'text'.")
        self.engine = None 

    def _speak_thread(self, text):
        try:
            # Initialize locally to avoid thread issues
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            pass

    def execute(self, text=None, payload=None):
        content = text or (payload.get('text') if payload else None)
        if not content:
            return "Error: No text to speak."
        
        # Run in thread so it doesn't block the agent
        t = threading.Thread(target=self._speak_thread, args=(content,))
        t.start()
        
        return f"Speaking: {content}"
