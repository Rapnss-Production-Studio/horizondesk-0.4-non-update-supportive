from core.sgi.skeleton import Organ, sgi_body

class VoiceBox(Organ):
    """
    Vocal Apparatus (TTS).
    """
    def __init__(self):
        super().__init__("Voice Box")
        
    def speak(self, text, emotion="Neutral"):
        # In deep implementation, this calls ElevenLabs/OpenAI TTS
        return f"🗣️ VOICE ({emotion}): '{text}'"

voice_box = VoiceBox()
sgi_body.add_organ(voice_box)
