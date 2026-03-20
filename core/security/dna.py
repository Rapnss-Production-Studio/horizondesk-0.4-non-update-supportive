import hashlib
import os
import sys
from core.security.neuro_crypt import shield

class GeneticSequencer:
    """
    Manages the 'Biological' Identity of the Codebase.
    Ensures that the code 'knows' which machine it lives on.
    """
    def __init__(self):
        self.host_id = shield._fingerprint # The Hardware Hash
        
    def generate_dna_marker(self):
        """
        Creates a cryptographic comment signature that is unique to this machine.
        This will be embedded into files by the Mutator.
        """
        # We start with the hardware ID
        dna = f"HORIZON-GENOME::{self.host_id}"
        # We salt it with a 'mutation' factor (randomness) but keep the root verifiable
        # Here we just sign it.
        signature = hashlib.sha256(dna.encode()).hexdigest()
        return f"# GENOME_ID: {signature[:16]} [DO NOT REMOVE]"

    def verify_dna(self, file_content):
        """
        Checks if a file belongs to this organism (machine).
        """
        # In a real polymorphic virus/agent, this would check if the marker matches
        # the current hardware ID.
        # For this stage, we verify structure.
        if "GENOME_ID" in file_content:
            # Check if it matches OUR signature? 
            # This is complex because mutations change.
            # We simple ensure it HAS a genome.
            return True
        return False
        
    def apoptosis(self):
        """
        Cellular Death. Called if deep integrity fails (Anti-Copy Trigger).
        """
        print("CRITICAL FAILURE: Genetic Mismatch. This code cannot run on this hardware.")
        # In a real scenario, this might delete sensitive keys or corrupt the main loop.
        sys.exit(666)

# Global DNA
dna_helix = GeneticSequencer()
