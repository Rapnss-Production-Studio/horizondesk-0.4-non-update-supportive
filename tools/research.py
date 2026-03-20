from core.tools import BaseTool
from core.llm import LLMProvider
from tools.web import SearchWebTool, DownloadPageTool
import json
import time

class DeepResearchTool(BaseTool):
    def __init__(self):
        super().__init__("DeepResearch", "Conducts deep research on a topic, browses multiple sources, and writes a report. Input: 'topic'.")
        self.llm = LLMProvider()
        self.search_tool = SearchWebTool()
        self.download_tool = DownloadPageTool()

    def execute(self, topic=None, payload=None):
        query = topic
        if payload and isinstance(payload, dict):
            query = payload.get('topic')
        elif payload:
             query = payload
             
        if not query: return "Error: Topic required."

        print(f"Starting Deep Research on: {query}...")
        
        # Step 1: Plan Search Queries
        plan_prompt = f"I need to research '{query}'. Generate 3 specific search queries to cover this topic comprehensively. Return ONLY a JSON list of strings."
        try:
            plan_resp = self._ask_llm(plan_prompt)
            # Try to parse list
            if "[" in plan_resp:
                queries = json.loads(plan_resp[plan_resp.find("["):plan_resp.rfind("]")+1])
            else:
                queries = [query, f"{query} details", f"{query} latest news"]
        except:
             queries = [query, f"{query} overview", f"{query} analysis"]

        # Step 2: Search and Gather Links
        sources = []
        for q in queries[:2]: # Limit to 2 queries for speed in this version
            print(f"Searching: {q}...")
            results = self.search_tool.execute(q)
            # Parse links (simple extraction from the text format returned by SearchTool)
            # Format is "Link: https://..."
            import re
            links = re.findall(r"Link: (https?://\S+)", results)
            for link in links[:2]: # Top 2 per query
                 if link not in [s['url'] for s in sources]:
                     sources.append({"url": link, "query": q})
        
        # Step 3: Browse and Summarize
        knowledge = []
        for src in sources:
            print(f"Reading: {src['url']}...")
            content = self.download_tool.execute(src['url'])
            if "Error" in content or len(content) < 100:
                continue
                
            summary_prompt = f"Summarize the following text relative to the topic '{query}'. Keep it dense and factual.\n\nText:\n{content[:4000]}"
            summary = self._ask_llm(summary_prompt)
            knowledge.append(f"Source: {src['url']}\nSummary: {summary}\n")
            
        if not knowledge:
            return "Failed to gather information. Web pages might be blocked or empty."

        # Step 4: Final Report
        print("Synthesizing Report...")
        full_context = "\n".join(knowledge)
        report_prompt = f"""You are a Research Assistant. Write a comprehensive report on '{query}' based on the following gathered notes.
        Start with an Executive Summary, then Key Findings, and a Conclusion. Cite sources where possible.

        Notes:
        {full_context}
        """
        report = self._ask_llm(report_prompt)
        
        return f"Research Report on {query}:\n\n{report}\n\n[Sources]\n" + "\n".join([s['url'] for s in sources])

    def _ask_llm(self, prompt):
        return self.llm.generate_text(prompt, system_prompt="You are a helpful research assistant. Output only the requested information.")
