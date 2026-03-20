import uuid
import time
import random
import hashlib
import threading

class HiveDrone:
    """
    A lightweight autonomous agent. 
    1. Polymorphic: Modifies its own memory footprint (padding) to be unique.
    2. Obedient but Safe: Only obeys cryptographically signed commands from the Queen.
    """
    def __init__(self, queen_public_key):
        self.id = str(uuid.uuid4())[:8]
        self.queen_key = queen_public_key
        self.status = "IDLE"
        self.polymorphic_pad = self._generate_padding()
        
    def _generate_padding(self):
        """Creates unique memory noise to avoid signature detection."""
        size = random.randint(1024, 4096)
        return random.randbytes(size)

    def verify_command(self, command, signature):
        """
        Byzantine Safety Check.
        Verify the command comes from the REAL Queen, not an imposter.
        """
        # Mock crypto verification using SHA256 of command + key
        expected = hashlib.sha256((command + self.queen_key).encode()).hexdigest()
        return signature == expected

    def execute(self, command, signature):
        if not self.verify_command(command, signature):
            self.status = "REJECTED_SECURITY_FAIL"
            return None
            
        self.status = "WORKING"
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.5))
        
        # Result logic
        result = f"Done: {command}"
        
        # "Ghost Protocol": Drones 'dissolve' after work to clean traces
        # (Reset padding)
        self.polymorphic_pad = self._generate_padding()
        self.status = "IDLE"
        return result
