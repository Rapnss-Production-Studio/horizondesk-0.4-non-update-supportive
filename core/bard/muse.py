import hashlib
import time
import os
import math
from core.security.neuro_crypt import shield

class TheMuse:
    """
    The Source of Inspiration.
    Uses Cryptographic System Noise + Hardware ID to generate 'Creative Seeds'.
    This ensures that Art created by this AI is unique to this Machine/Soul.
    """
    def __init__(self):
        shield.check_integrity()
        self.soul_hash = shield._fingerprint
        
    def summon_inspiration(self, context="generic"):
        """
        Generates a float (0.0 - 1.0) and a seed string based on chaos.
        """
        timestamp = str(time.time())
        entropy = os.urandom(32).hex()
        
        raw = f"{self.soul_hash}::{context}::{timestamp}::{entropy}"
        seed_hash = hashlib.sha512(raw.encode()).hexdigest()
        
        # Convert first 8 chars to float
        val = int(seed_hash[:8], 16) / 0xFFFFFFFF
        
        return {
            "val": val, 
            "seed": seed_hash,
            "chaos_factor": math.sin(val * math.pi) # Wave function of creativity
        }

# Singleton
muse = TheMuse()
