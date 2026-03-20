import speech_recognition as sr
import pyttsx3
import threading
import time
from colorama import Fore

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS
        voices = self.tts_engine.getProperty('voices')
        # Try to find a female voice or a good English voice
        for voice in voices:
            if "david" not in voice.name.lower() and "zira" in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        self.tts_engine.setProperty('rate', 170) # Faster talking

        # Adjust for ambient noise
        with self.microphone as source:
            print(Fore.YELLOW + "[Voice] Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print(Fore.GREEN + "[Voice] Ready.")

    def speak(self, text):
        """Non-blocking speak"""
        def _run():
            try:
                # Re-init for thread safety if needed, but pyttsx3 usually handles it
                # self.tts_engine.say(text) # This can be buggy in threads
                # Use a fresh engine for reliable threading
                engine = pyttsx3.init()
                engine.setProperty('rate', 170)
                engine.say(text)
                engine.runAndWait()
            except:
                pass
        
        # Print what is being said
        print(Fore.CYAN + f"[Voice Output]: {text}")
        t = threading.Thread(target=_run)
        t.start()
        # t.join() # If we want blocking

    def listen(self, timeout=5):
        """Listens for a command."""
        with self.microphone as source:
            print(Fore.BLUE + "[Voice] Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print(Fore.BLUE + "[Voice] Processing...")
                text = self.recognizer.recognize_google(audio)
                print(Fore.WHITE + f"[User Said]: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except Exception as e:
                print(Fore.RED + f"[Voice Error]: {e}")
                return None

    def listen_for_wake_word(self, wake_word="omni"):
        """Blocking loop until wake word is heard."""
        print(Fore.YELLOW + f"[Voice] Waiting for wake word '{wake_word}'...")
        while True:
            text = self.listen(timeout=None) # No timeout, just wait
            if text and wake_word.lower() in text.lower():
                self.speak("I'm listening.")
                return True
