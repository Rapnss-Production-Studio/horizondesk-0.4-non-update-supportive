import os
from core.tools import BaseTool

class ListDirectoryTool(BaseTool):
    def __init__(self):
        super().__init__("ListDirectory", "Lists files in a given directory path. Input should be a JSON with key 'path'.")

    def execute(self, path=None, payload=None):
        target_path = path or payload
        if not target_path:
             return "Error: No path provided."
        
        # Clean path
        target_path = target_path.strip().strip('"').strip("'")
        
        # Basic security: ensure valid path exists
        if not os.path.exists(target_path):
            return f"Error: Path '{target_path}' does not exist."
            
        try:
            items = os.listdir(target_path)
            return str(items[:50]) + ("..." if len(items) > 50 else "") # Truncate for token limit
        except Exception as e:
            return f"Error listing directory: {e}"

class ReadFileTool(BaseTool):
    def __init__(self):
        super().__init__("ReadFile", "Reads content of a text file. Input: JSON with key 'path'.")

    def execute(self, path=None, payload=None):
        target_path = path or payload
        if not target_path: return "Error: No path provided."
        target_path = target_path.strip().strip('"').strip("'")
        
        if not os.path.exists(target_path):
             return f"Error: File '{target_path}' not found."
        
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:2000] + ("\n...[truncated]" if len(content) > 2000 else "")
        except Exception as e:
            return f"Error reading file: {e}"

class WriteFileTool(BaseTool):
    def __init__(self):
        super().__init__("WriteFile", "Writes content to a file. Input: JSON with keys 'path' and 'content'. For multi-line content, use escaped newlines (\\\\n).")

    def execute(self, path=None, content=None, payload=None):
        if payload and isinstance(payload, dict):
            path = payload.get('path')
            content = payload.get('content')
        elif payload and isinstance(payload, str):
            # Try to extract path and content from malformed string
            # Sometimes LLM sends the whole thing as a string
            import re
            path_match = re.search(r'"path"\s*:\s*"([^"]+)"', payload)
            content_match = re.search(r'"content"\s*:\s*"(.*)"', payload, re.DOTALL)
            if path_match:
                path = path_match.group(1)
            if content_match:
                content = content_match.group(1)
            
        if not path or content is None:
            return "Error: path and content required. Use format: {\"path\": \"...\", \"content\": \"...\"}"
            
        path = str(path).strip().strip('"').strip("'")
        
        # Handle escaped characters in content
        if isinstance(content, str):
            # Convert escaped newlines to actual newlines
            content = content.replace('\\n', '\n')
            content = content.replace('\\t', '\t')
            # Handle double-escaped backslashes
            content = content.replace('\\\\', '\\')
        
        try:
            # Ensure directory exists
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

