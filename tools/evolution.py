from core.tools import BaseTool
import os
import shutil
from core.llm import LLMProvider

class EvolveCodeTool(BaseTool):
    def __init__(self):
        super().__init__("EvolveCode", "Modifies the Agent's own source code. Input: 'file_path', 'instruction'. BACKS UP file first.")
        self.llm = LLMProvider()

    def execute(self, file_path=None, instruction=None, payload=None):
        fp = file_path
        instr = instruction
        
        if payload and isinstance(payload, dict):
            fp = payload.get('file_path')
            instr = payload.get('instruction')
            
        if not fp or not instr:
            return "Error: 'file_path' and 'instruction' required."
            
        # Security Check: Only allow editing files in the project directory
        # This is a loose check, but prevents editing C:\Windows at least
        if "Horizon desk" not in fp and "Horizon desk" not in os.getcwd():
             return "Error: Security Restriction. You can only edit files within the Horizon Desk project."

        if not os.path.exists(fp):
            return f"Error: File not found: {fp}"

        # 1. Backup
        backup_path = fp + ".bak"
        try:
            shutil.copy2(fp, backup_path)
            print(f"[Evolution] Backup created at {backup_path}")
        except Exception as e:
            return f"Error creating backup: {e}"

        # 2. Read Original
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            return f"Error reading file: {e}"

        # 3. Generate New Code
        prompt = f"""You are a Senior Python Architect.
        Current Code ({fp}):
        ```python
        {original_code}
        ```
        
        Instruction for Improvement/Modification:
        {instr}
        
        Return ONLY the full updated code block. No explanation.
        """
        
        try:
            print(f"[Evolution] Evolving {fp}...")
            new_code_raw = self.llm.generate_text(prompt, system_prompt="Output only valid python code.")
            
            # Extract code from markdown blocks if present
            new_code = new_code_raw
            if "```python" in new_code_raw:
                new_code = new_code_raw.split("```python")[1].split("```")[0]
            elif "```" in new_code_raw:
                new_code = new_code_raw.split("```")[1].split("```")[0]
                
            new_code = new_code.strip()
            
            # Basic validation
            if len(new_code) < 10:
                return "Error: Generated code seems too short or invalid."

            # 4. Write New Code
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(new_code)
                
            return f"Evolution Complete. {fp} has been updated. Backup saved."
            
        except Exception as e:
            # Restore backup on failure?
            return f"Error during evolution: {e}"
