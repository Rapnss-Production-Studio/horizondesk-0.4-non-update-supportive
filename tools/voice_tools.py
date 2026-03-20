from core.tools import BaseTool
from core.voice import VoiceEngine
from core.llm import LLMProvider
import time

# Global Voice Engine (Lazy load)
voice_engine = None

class VoiceLoopTool(BaseTool):
    def __init__(self):
        super().__init__("StartVoiceMode", "Enters Hands-Free Voice Mode. The agent will listen for commands verbally.")
        self.llm = LLMProvider()

    def execute(self, payload=None):
        global voice_engine
        if not voice_engine:
            voice_engine = VoiceEngine()
            
        voice_engine.speak("Voice mode activated. Say 'Exit' to stop.")
        
        # Simple REPL logic inside the tool (Experimental)
        # Note: In a real architecture, this should be in main.py, but for now we encapsulate it here
        # to allow 'switching' into it via a tool call.
        
        active = True
        while active:
            user_text = voice_engine.listen(timeout=5)
            
            if user_text:
                if "exit" in user_text.lower() or "stop" in user_text.lower():
                    voice_engine.speak("Stopping voice mode.")
                    active = False
                    break
                
                # Simple Chat Response loop for now (Fast Path)
                # Ideally, we would recurse back to the Agent, but that creates recursion depth issues.
                # Use a lightweight conversational loop here.
                prompt = f"User said via voice: '{user_text}'. Respond briefly (1-2 sentences) or acknowledge."
                response = self.llm.generate_text(prompt)
                voice_engine.speak(response)
                
            time.sleep(0.5)
            
        return "Voice Mode Ended."
