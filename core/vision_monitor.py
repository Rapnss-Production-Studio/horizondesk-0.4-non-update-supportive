import time
import pyautogui
import os
import uuid
from core.llm import LLMProvider
from colorama import Fore

class VisionMonitor:
    def __init__(self):
        self.llm = LLMProvider()
        # Ensure screenshot dir exists
        home = os.path.expanduser("~")
        self.screenshot_dir = os.path.join(os.environ.get('USERPROFILE', home), "AppData", "Local", "Omniagent", "VisionMonitor")
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def watch_for_visual_event(self, description, timeout=300, check_interval=5):
        """
        Watches the screen until the visual event described is detected or timeout occurs.
        Returns True if detected, False if timeout.
        """
        start_time = time.time()
        print(Fore.CYAN + f"[The Eye] Watching screen for: '{description}' (Timeout: {timeout}s)")
        
        while (time.time() - start_time) < timeout:
            # 1. Take Screenshot
            filename = os.path.join(self.screenshot_dir, "monitor_frame.png")
            pyautogui.screenshot(filename)
            
            # 2. Analyze with VLM
            try:
                # Optimized prompt for YES/NO
                prompt = f"Look at this screenshot. Is the following visual event happening or present: '{description}'?\nRespond with ONLY 'YES' or 'NO'."
                result = self.llm.analyze_image(filename, prompt=prompt)
                
                print(Fore.BLUE + f"[The Eye] Analysis: {result}")
                
                if "YES" in result.upper():
                    print(Fore.GREEN + f"[The Eye] Visual Event Detected: {description}")
                    return True
            except Exception as e:
                print(Fore.RED + f"[The Eye] Error: {e}")
            
            # 3. Wait
            time.sleep(check_interval)
            
        print(Fore.YELLOW + f"[The Eye] Timed out waiting for: {description}")
        return False
