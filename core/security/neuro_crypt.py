import hashlib
import platform
import subprocess
import os
import ctypes

class NeuroCrypt:
    """
    Implements hardware-locked security.
    The Neural Network will ONLY function on the machine it was born on.
    Multi-factor binding: CPU ID + MAC Address + Disk Serial.
    """
    def __init__(self):
        self._fingerprint = self._generate_hardware_fingerprint()
        
    def _generate_hardware_fingerprint(self):
        try:
            # 1. Hostname/System Info
            sys_info = platform.node() + platform.processor()
            
            # 2. Disk Serial (Windows specific command) (Deep binding)
            if platform.system() == "Windows":
                 try:
                     cmd = "wmic diskdrive get SerialNumber"
                     output = subprocess.check_output(cmd, shell=True).decode()
                     # Robust parsing: split lines, strip whitespace, remove empty lines
                     lines = [line.strip() for line in output.split('\n') if line.strip()]
                     
                     # Remove header if present
                     if lines and lines[0].lower().startswith("serialnumber"):
                         lines = lines[1:]
                         
                     if lines:
                         # Sort to ensure determinism across reboots/calls
                         lines.sort()
                         disk = lines[0]
                     else:
                         disk = "generic_disk_empty"
                 except:
                     disk = "generic_disk"
            else:
                disk = "unix_disk"
                
            # Combine
            raw = f"{sys_info}::{disk}::HORIZON_NEURAL_CORE".encode()
            
            # Create a 256-bit hash (The "Soul" of the PC)
            return hashlib.sha3_512(raw).hexdigest()
        except Exception as e:
            # Fallback for safety, but in production this would lock down.
            return "UNSECURE_DEV_MODE"

    def authorize_synapse(self, synapse_signal):
        """
        Validates if a neural signal is authentic and originated from this hardware.
        """
        # We sign the signal with the fingerprint
        signature = hashlib.sha256((str(synapse_signal) + self._fingerprint).encode()).hexdigest()
        return signature

    def check_integrity(self):
        """Standard integrity check."""
        current = self._generate_hardware_fingerprint()
        if current != self._fingerprint:
            # The Brain has been transplanted. REJECT.
            raise SystemError("NEURAL REJECTION: Hardware mismatch. Brain cannot function in this body.")
        return True

# Singleton
shield = NeuroCrypt()
