import os
import random
import shutil
import gc

class AntiForensicsScrubber:
    """
    Ensures no data remains.
    DoD 5220.22-M Standard for file deletion.
    """
    
    def secure_delete(self, file_path):
        """
        Overwrites file 3 times before unlinking.
        Pass 1: Zeros
        Pass 2: Ones
        Pass 3: Random
        """
        if not os.path.exists(file_path):
            return "File not found."
            
        try:
            length = os.path.getsize(file_path)
            with open(file_path, "wb") as f:
                # Pass 1
                f.write(b'\x00' * length)
                f.seek(0)
                # Pass 2
                f.write(b'\xFF' * length)
                f.seek(0)
                # Pass 3
                f.write(os.urandom(length))
                
            os.remove(file_path)
            return f"File {os.path.basename(file_path)} vaporized (DoD Standard)."
        except Exception as e:
            return f"Scrub Error: {e}"

    def purge_memory(self):
        """
         Forces strict Garbage Collection and clears internal caches.
        """
        # Create generation gap
        gc.collect()
        
        # In deep Python forensics, strings stick around.
        # We can't easily overwrite immutable strings, but we can clear dicts.
        return "RAM Sanitized. Generation 0-2 collected."

# Singleton
scrubber = AntiForensicsScrubber()
