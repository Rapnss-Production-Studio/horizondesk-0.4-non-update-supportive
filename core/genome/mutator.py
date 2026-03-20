import ast
import random
import os
import time
from core.security.dna import dna_helix

class CodeMutator:
    """
    The Evolutionary Engine. 
    Safely modifies source code to:
    1. Change file signatures (Polymorphism).
    2. Embed Hardware DNA (Security).
    """
    
    def mutate_file(self, file_path):
        """
        Read -> Mutate -> Verify -> Write.
        Returns: Success (bool), Message
        """
        if not os.path.exists(file_path):
            return False, "File not found."
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            # 1. Integrity Check: Can we parse the original?
            try:
                tree = ast.parse(source)
            except SyntaxError:
                return False, "Original file has syntax errors. Aborting mutation."

            # 2. Mutation: Inject 'Junk DNA' (Polymorphic Comments)
            # We add a unique, hardware-bound signature to the end or start.
            
            # Remove old DNA if present to avoid clutter
            lines = source.splitlines()
            clean_lines = [l for l in lines if "GENOME_ID" not in l]
            
            # Generate new DNA
            new_dna = dna_helix.generate_dna_marker()
            
            # inject at a random harmless location (end of file is safest)
            clean_lines.append("")
            clean_lines.append(new_dna)
            clean_lines.append(f"# Mutation Timestamp: {time.time()}")
            
            mutated_source = "\n".join(clean_lines)
            
            # 3. SAFETY: Verify Syntax of Mutated Code
            try:
                ast.parse(mutated_source)
            except SyntaxError as e:
                return False, f"Mutation failed syntax check: {e}"
                
            # 4. Write
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(mutated_source)
                
            return True, f"File {file_path} successfully mutated with DNA."

        except Exception as e:
            return False, f"Critical Mutation Error: {e}"

    def recursive_mutation(self, directory):
        """Mutates all python files in a directory."""
        report = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and "venv" not in root:
                    path = os.path.join(root, file)
                    success, msg = self.mutate_file(path)
                    report.append(msg)
        return report

# Singleton
mutator = CodeMutator()
