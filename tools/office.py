from core.tools import BaseTool
import os

class GenerateHTMLDocumentTool(BaseTool):
    def __init__(self):
        super().__init__("GenerateHTMLDocument", "Creates a styled HTML document. Input: JSON 'title', 'content', 'filename'.")

    def execute(self, title="Document", content="", filename=None, payload=None):
        if payload and isinstance(payload, dict):
            title = payload.get('title', title)
            content = payload.get('content', content)
            filename = payload.get('filename')

        if not filename: return "Error: filename required."
        if not filename.endswith(".html"): filename += ".html"
        
        # User Home/Desktop
        base_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(base_dir, filename)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                p {{ margin-bottom: 20px; }}
                .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                {content}
            </div>
        </body>
        </html>
        """
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            return f"Document saved to {path}. You can open it in Chrome and Print to PDF."
        except Exception as e:
            return f"Error creating doc: {e}"

# Future: Add Google Sheets via API (Complex, requires OAuth credentials json)
# For now, we stick to local file generation.
