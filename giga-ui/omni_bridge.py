
import os
import subprocess
import threading
import time
import sys
import re

# Project Root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

class OmniagentBridge:
    """Bridge to communicate with main.py Omniagent via Streaming"""
    
    def __init__(self):
        self.process = None
        self.lock = threading.Lock()
        self.on_output = None
        self.running = False
    
    def start(self, on_output_callback):
        """Start the main.py omniagent subprocess"""
        self.on_output = on_output_callback
        try:
            main_py = os.path.join(PROJECT_ROOT, 'main.py')
            if not os.path.exists(main_py):
                print(f"⚠ main.py not found at {main_py}")
                return False
            
            # Start main.py subprocess
            # Use -u for unbuffered output
            self.process = subprocess.Popen(
                [sys.executable, '-u', main_py],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stderr to stdout
                cwd=PROJECT_ROOT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.running = True
            
            # Start reader thread
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            
            print("✓ Omniagent subprocess started (Stream Mode)")
            return True
        except Exception as e:
            print(f"⚠ Failed to start Omniagent: {e}")
            return False
            
    def _read_loop(self):
        """Continuously read stdout character-by-character and call callback"""
        while self.running and self.process:
            try:
                # Read 1 byte at a time to support prompts without newlines
                char = self.process.stdout.read(1)
                if not char and self.process.poll() is not None:
                    break
                
                if char:
                    # We send raw characters and let the UI handle buffering/ANSI
                    if self.on_output:
                        self.on_output(char)
            except Exception as e:
                # print(f"Error in read loop: {e}")
                break
        
    def write(self, text):
        """Send text to Omniagent stdin"""
        if not self.process or self.process.poll() is not None:
             if self.on_output:
                 self.on_output("[System] Process not running. Restarting...")
             self.start(self.on_output)
        
        try:
            with self.lock:
                self.process.stdin.write(text + "\n")
                self.process.stdin.flush()
        except Exception as e:
            if self.on_output:
                self.on_output(f"[System] Error writing: {e}")
    
    def _clean_ansi(self, text):
        """Remove ANSI escape sequences"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def stop(self):
        """Stop the Omniagent subprocess"""
        self.running = False
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
