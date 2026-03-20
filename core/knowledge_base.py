import json
import os
import time
import uuid
from core.llm import LLMProvider

class KnowledgeBase:
    def __init__(self):
        home = os.path.expanduser("~")
        self.data_dir = os.path.join(os.environ.get('USERPROFILE', home), "AppData", "Local", "Omniagent", "Brain")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.kb_file = os.path.join(self.data_dir, "knowledge_base.json")
        self.kb = self._load_kb()
        self.llm = LLMProvider()

    def _load_kb(self):
        if os.path.exists(self.kb_file):
            try:
                with open(self.kb_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_kb(self):
        with open(self.kb_file, 'w') as f:
            json.dump(self.kb, f, indent=2)

    def learn_content(self, title, content, source="User"):
        """Analyzes and stores content with semantic tags."""
        # 1. Generate Metadata using LLM
        prompt = f"""Analyze the following text and generate:
        1. A brief summary (1 sentence).
        2. A list of 5-10 relevant tags/keywords (comma separated).
        
        Text:
        {content[:2000]}
        """
        try:
            analysis = self.llm.generate_text(prompt, system_prompt="You are a librarian. Output strict semantic metadata.").strip()
            # Simple parsing (robustness improvements can be added)
            if "Summary:" in analysis:
                summary = analysis.split("Summary:")[1].split("Tags:")[0].strip()
                tags = analysis.split("Tags:")[1].strip()
            else:
                summary = " Content stored."
                tags = "general"
        except:
            summary = "Content stored."
            tags = "general"

        entry = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "summary": summary,
            "tags": tags.lower(),
            "source": source,
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d")
        }
        
        self.kb.append(entry)
        self.save_kb()
        return f"Learned '{title}'.\nSummary: {summary}\nTags: {tags}"

    def query(self, query):
        """Retrieves content based on simple relevance scoring against tags/summary."""
        query_terms = query.lower().split()
        results = []
        
        for entry in self.kb:
            score = 0
            # Weighted scoring
            text_to_search = f"{entry['title']} {entry['tags']} {entry['summary']}".lower()
            
            for term in query_terms:
                if term in text_to_search:
                    score += 1
                if term in entry['title'].lower(): # Boost title matches
                    score += 2
            
            if score > 0:
                results.append((score, entry))
        
        # Sort by score desc
        results.sort(key=lambda x: x[0], reverse=True)
        
        if not results:
            return "No relevant knowledge found."
            
        output = [f"Found {len(results)} matches for '{query}':"]
        for score, entry in results[:3]: # Top 3
            output.append(f"\n[Title]: {entry['title']} (Score: {score})")
            output.append(f"[Summary]: {entry['summary']}")
            output.append(f"[Content Snippet]: {entry['content'][:200]}...")
        
        return "\n".join(output)
