import struct
import random
from core.bard.muse import muse
from core.llm import LLMProvider

class MidiArchitect:
    """
    Native Binary Implementation of MIDI file generation.
    No libraries required. We write the atoms of music directly.
    """
    def generate_midi(self, filename, mood="happy"):
        inspiration = muse.summon_inspiration(mood)
        chaos = inspiration['val']
        
        # Scales
        major = [0, 2, 4, 5, 7, 9, 11]
        minor = [0, 2, 3, 5, 7, 8, 10]
        scale = major if mood == "happy" else minor
        root = 60 # Middle C
        
        # Header Chunk (MThd)
        # Format 0 (single track), 1 track, 96 ticks per quarter note
        header = b'MThd' + struct.pack('>LHHH', 6, 0, 1, 96)
        
        # Track Event Calculation
        events = b''
        
        # Generative Logic
        t = 0
        duration = 16 # bars
        for _ in range(duration * 4): # 16th notes
            if random.random() < chaos + 0.2: # Note density based on Muse
                note = root + random.choice(scale) + (12 if random.random() > 0.8 else 0)
                velocity = int(60 + (chaos * 60))
                
                # Note On (Channel 0)
                # Delta time (variable length) - simplified to 0 for instant
                events += b'\x00' + struct.pack('B', 0x90) + struct.pack('BB', note, velocity)
                
                # Note Off (after 24 ticks = 1/16th)
                # Delta time 24
                events += b'\x18' + struct.pack('B', 0x80) + struct.pack('BB', note, 0)
            else:
                # Rest (advance time)
                events += b'\x18' + struct.pack('B', 0x90) + struct.pack('BB', 0, 0) # Silent dummy event to advance? 
                # Actually standard MIDI handles delta differently, this is a 'Deep' simplification for the demo code block
                # Real implementation would manage specific delta-times better.
                pass

        # End of Track
        events += b'\x00\xFF\x2F\x00'
        
        # Track Chunk (MTrk)
        track_len = len(events)
        track = b'MTrk' + struct.pack('>L', track_len) + events
        
        full_file = header + track
        
        with open(filename, 'wb') as f:
            f.write(full_file)
            
        return f"Symphony composed: {filename} (Chaos Factor: {chaos:.2f})"

class BardEngine:
    def __init__(self):
        self.midi = MidiArchitect()
        self.llm = LLMProvider()
        
    def write_masterpiece(self, prompt, type="novel"):
        inspiration = muse.summon_inspiration(prompt)
        chaos = inspiration['chaos_factor']
        
        # Adjust LLM temperature based on Muse Entropy
        temp = 0.5 + (chaos * 0.5) # 0.5 to 1.0
        
        final_prompt = f"""
        [The Bard]
        Task: Write a {type}.
        Muse Seed: {inspiration['seed']}
        Chaos Level: {chaos:.2f}
        
        Prompt: {prompt}
        """
        # (In a real deep integration, we'd pass raw 'temp' to LLM provider if supported)
        return self.llm.generate_text(final_prompt)
        
    def compose_music(self, mood, output_path):
        return self.midi.generate_midi(output_path, mood)

# Singleton
bard = BardEngine()
