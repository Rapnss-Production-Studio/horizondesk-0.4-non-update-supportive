from core.tools import BaseTool
from core.genome.mutator import mutator
import os

class MutateSelfTool(BaseTool):
    def __init__(self):
        super().__init__("MutateSelf", "Triggers a Polymorphic Mutation of the agent's codebase. Embeds Hardware DNA. Input: 'target_path' (optional, defaults to current project).")

    def execute(self, target_path=None, payload=None):
        path = target_path or os.getcwd()
        if payload and payload.get('target_path'):
            path = payload.get('target_path')
            
        # Security: restrict to project
        if "Horizon desk" not in path:
            return "Error: Security Restriction. Can only mutate internal cells."
            
        results = mutator.recursive_mutation(path)
        return f"Mutation Cycle Complete. {len(results)} files processed.\nFirst 3 results: {results[:3]}"
