import random
import math

class QBit:
    """
    Represents a unit of 'Thought' in a Superposition state.
    Instead of Yes/No, it holds a Probability Amplitude.
    """
    def __init__(self, name, probability=0.5):
        self.name = name
        self.alpha = math.sqrt(1 - probability) # |0> state amplitude
        self.beta = math.sqrt(probability)      # |1> state amplitude
        self.entangled_with = [] # List of other QBits (Spooky Action at a Distance)
    
    def entangle(self, other_qbit):
        """Links this thought to another. If one collapses, the other is affected."""
        self.entangled_with.append(other_qbit)
        other_qbit.entangled_with.append(self)
        
    def measure(self):
        """
        Collapse the wave function.
        Returns True (1) or False (0) based on probability amplitude.
        Simultaneously affects entangled QBits.
        """
        # Born rule: Probability = |beta|^2
        p_1 = abs(self.beta) ** 2
        outcome = random.random() < p_1
        
        # Propagate collapse (Deep Complexity)
        for q in self.entangled_with:
            q.collapse_influence(outcome)
            
        return outcome

    def collapse_influence(self, partner_outcome):
        """
        Received a collapse signal from an entangled particle.
        This shifts our probability.
        """
        # If entangled thought executed, bias this one.
        if partner_outcome:
            # Shift towards 1 (constructive interference)
            self.beta = min(1.0, self.beta * 1.2)
        else:
            # Shift towards 0 (destructive interference)
            self.beta = max(0.0, self.beta * 0.8)
            
    def __repr__(self):
        p = abs(self.beta) ** 2
        return f"QBit({self.name} | P={p:.2f})"
