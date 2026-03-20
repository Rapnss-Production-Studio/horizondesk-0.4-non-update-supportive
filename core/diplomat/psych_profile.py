from core.llm import LLMProvider

class PsychProfiler:
    """
    Analyzes text to determine the Psychological Profile of the interlocutor.
    Uses the OCEAN (Big Five) Model.
    """
    def __init__(self):
        self.llm = LLMProvider()
        
    def analyze_profile(self, text_sample):
        """
        Returns a dictionary of traits and recommended strategy.
        """
        prompt = f"""
        [Psychological Analysis Task]
        Target Text: "{text_sample}"
        
        Task:
        1. Rate the author on the Big Five scales (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) from 0-10.
        2. Based on the highest traits, select the best Rhetorical Strategy:
           - LOGOS (Logic/Data) -> High Conscientiousness
           - PATHOS (Emotion/Story) -> High Agreeableness/Neuroticism
           - ETHOS (Credibility/Status) -> High Extraversion
           
        Return ONLY a JSON: {{"traits": {{...}}, "strategy": "LOGOS/PATHOS/ETHOS", "explanation": "..."}}
        """
        try:
            return self.llm.generate_text(prompt, system_prompt="Output valid JSON only.")
        except:
             return {"traits": {}, "strategy": "LOGOS", "explanation": "Defaulting to Logic."}

# Singleton
profiler = PsychProfiler()
