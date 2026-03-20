from core.tools import BaseTool
import os

class AnalyzeImageTool(BaseTool):
    def __init__(self, agent):
        super().__init__("AnalyzeImage", "Analyzes a screenshot/image to answer a question. Input: JSON with 'filename' (optional) and 'question'.")
        self.agent = agent

    def execute(self, filename=None, question=None, payload=None):
        if payload and isinstance(payload, dict):
            filename = payload.get('filename')
            question = payload.get('question')
        
        if not question:
            return "Error: Question required."
            
        # Resolve filename
        user_profile = os.environ.get('USERPROFILE') or "C:\\Users\\User"
        base_dir = os.path.join(user_profile, "AppData", "Local", "Omniagent", "Screenshot")
        
        if not filename:
            # Find most recent screenshot
            import glob
            files = glob.glob(os.path.join(base_dir, "*.png"))
            if not files:
                return "Error: No screenshots found."
            filename = max(files, key=os.path.getmtime)
        elif not os.path.isabs(filename):
            filename = os.path.join(base_dir, filename)
            
        if not os.path.exists(filename):
            return f"Error: File {filename} not found."
            
        try:
            # Use the agent's LLM provider
            response = self.agent.llm.analyze_image(filename, question)
            return f"Analysis of {os.path.basename(filename)}: {response}"
        except Exception as e:
            return f"Error analyzing image: {e}"

class LocateObjectTool(BaseTool):
    def __init__(self, agent):
        super().__init__("LocateObject", "Locates an object on screen using grid classification. Input: JSON 'object_name' (e.g. 'login button'). Returns approximate coordinates.")
        self.agent = agent

    def execute(self, object_name=None, payload=None):
        target = object_name or payload
        if isinstance(target, dict): target = target.get('object_name')
        if not target: return "Error: No object name provided."
        
        # 1. Take Screenshot
        import pyautogui
        import os
        import time
        from PIL import Image
        import shutil
        
        # Helper to crop
        def crop_grid(img_path, rows=3, cols=3):
            img = Image.open(img_path)
            w, h = img.size
            chunk_w = w // cols
            chunk_h = h // rows
            chunks = []
            for r in range(rows):
                for c in range(cols):
                    box = (c * chunk_w, r * chunk_h, (c + 1) * chunk_w, (r + 1) * chunk_h)
                    chunk = img.crop(box)
                    chunks.append({
                        "id": f"{r}_{c}",
                        "img": chunk,
                        "center": (c * chunk_w + chunk_w // 2, r * chunk_h + chunk_h // 2),
                        "box": box
                    })
            return chunks

        try:
            # Capture full screen
            user_profile = os.environ.get('USERPROFILE') or "C:\\Users\\User"
            base_dir = os.path.join(user_profile, "AppData", "Local", "Omniagent", "Vision")
            if not os.path.exists(base_dir): os.makedirs(base_dir)
            
            # Timestamped screenshot
            timestamp = int(time.time())
            full_shot = os.path.join(base_dir, f"search_full_{timestamp}.png")
            pyautogui.screenshot().save(full_shot)
            
            # Divide into 3x3 grid
            chunks = crop_grid(full_shot, 3, 3)
            
            best_chunk = None
            highest_score = 0
            
            print(f"Scanning 9 chunks for '{target}'...")
            
            # Analyze each chunk
            for chunk in chunks:
                chunk_path = os.path.join(base_dir, f"chunk_{timestamp}_{chunk['id']}.jpg")
                chunk['img'].save(chunk_path)
                
                # Classify
                result = self.agent.llm.classify_image(chunk_path)
                
                # ResNet output format check
                # Typically list of dicts: [ { label: "...", score: ... }, ... ]
                if isinstance(result, list):
                    for item in result:
                        label = str(item.get('label', '')).lower()
                        score = float(item.get('score', 0))
                        
                        # Simple keyword match
                        if target.lower() in label:
                            print(f"Match: {label} ({score:.2f}) in chunk {chunk['id']}")
                            if score > highest_score:
                                highest_score = score
                                best_chunk = chunk
                
                # Cleanup chunk file to save space? Keep for debugging for now.
            
            if best_chunk and highest_score > 0.05: # Low threshold for ResNet basic classes
                x, y = best_chunk['center']
                return f"Found '{target}' in chunk {best_chunk['id']} (approx center: {x}, {y}). Score: {highest_score:.2f}"
            else:
                 return f"Could not locate '{target}' with high confidence. Best score: {highest_score}"
                 
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error locating object: {e}"
