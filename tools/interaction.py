import pyautogui
import time
import math
import random
from core.tools import BaseTool

class HumanMoveTool(BaseTool):
    def __init__(self):
        super().__init__("HumanMove", "Moves mouse naturally (Bezier curve) to x,y. Good for drawing/UI. Input: 'x', 'y'.")

    def _bezier_point(self, t, p0, p1, p2):
        return (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2

    def execute(self, x=None, y=None, payload=None):
        if payload and isinstance(payload, dict):
            x = payload.get('x')
            y = payload.get('y')
            
        if x is None or y is None: return "Error: Coordinates required."
        
        try:
            end_x, end_y = int(x), int(y)
            start_x, start_y = pyautogui.position()
            
            # Control Point for Curve (Randomized offset)
            control_x = (start_x + end_x) / 2 + random.randint(-100, 100)
            control_y = (start_y + end_y) / 2 + random.randint(-100, 100)
            
            # Steps
            steps = 20
            for i in range(steps):
                t = i / steps
                bx = self._bezier_point(t, start_x, control_x, end_x)
                by = self._bezier_point(t, start_y, control_y, end_y)
                pyautogui.moveTo(bx, by)
                time.sleep(0.005) # Speed control
                
            pyautogui.moveTo(end_x, end_y) # Ensure final precision
            return f"Moved smoothly to {x}, {y}"
        except Exception as e:
            return f"Error moving: {e}"

class ComplexDragTool(BaseTool):
    def __init__(self):
        super().__init__("ComplexDrag", "Precise Drag-and-Drop. Input: 'from_x', 'from_y', 'to_x', 'to_y', 'duration' (seconds).")

    def execute(self, from_x=None, from_y=None, to_x=None, to_y=None, duration=1.0, payload=None):
        if payload and isinstance(payload, dict):
            from_x = payload.get('from_x')
            from_y = payload.get('from_y')
            to_x = payload.get('to_x')
            to_y = payload.get('to_y')
            duration = payload.get('duration', 1.0)

        if not all([from_x, from_y, to_x, to_y]):
             return "Error: All coordinates (from/to) required."

        try:
            start_x, start_y = int(from_x), int(from_y)
            end_x, end_y = int(to_x), int(to_y)
            
            pyautogui.moveTo(start_x, start_y)
            time.sleep(0.2)
            pyautogui.mouseDown()
            time.sleep(0.1)
            pyautogui.moveTo(end_x, end_y, duration=float(duration))
            time.sleep(0.1)
            pyautogui.mouseUp()
            
            return f"Dragged from {start_x},{start_y} to {end_x},{end_y}"
        except Exception as e:
            return f"Error dragging: {e}"
