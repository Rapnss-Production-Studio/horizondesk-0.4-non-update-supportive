import os
import json
from core.tools import BaseTool
from collections import defaultdict
import datetime

class VideoEditorTool(BaseTool):
    """
    A unified powerful tool to edit videos using Python MoviePy.
    """
    def __init__(self):
        super().__init__(
            name="VideoEditorTool",
            description="Use MoviePy to edit videos programmatically. Perform cuts, concatenate videos, or add text."
        )

    def get_schema(self):
        return f"""
============= {self.name} =============
{self.description}

Action Value: {self.name}
Action Input Format:
{{
  "task": "cut" | "concatenate" | "add_text",
  "input_paths": ["full/path/to/vid1.mp4", ...],
  "output_path": "full/path/to/output.mp4",
  
  // Optional for 'cut':
  "start_time": 0 (seconds),
  "end_time": 5 (seconds),
  
  // Optional for 'add_text':
  "text": "Hello World",
  "fontsize": 50,
  "color": "white"
}}
==========================================
"""

    def execute(self, **kwargs):
        try:
            import moviepy.editor as mp
        except ImportError:
            return "Error: 'moviepy' is not installed. Please run 'pip install moviepy' in the terminal."

        task = kwargs.get("task")
        input_paths = kwargs.get("input_paths", [])
        output_path = kwargs.get("output_path", "output.mp4")

        # Validate Paths
        if not task:
            return "Error: You must provide a 'task' (cut, concatenate, add_text)."
        if not input_paths:
            return "Error: You must provide at least one 'input_path' in a list."
            
        # Ensure input exists
        for path in input_paths:
            if not os.path.exists(path):
                return f"Error: Input video '{path}' does not exist on disk."

        try:
            if task == "cut":
                start = kwargs.get("start_time", 0)
                end = kwargs.get("end_time")
                if not end:
                    return "Error: 'end_time' is required for cutting."
                    
                clip = mp.VideoFileClip(input_paths[0])
                subclip = clip.subclip(start, end)
                subclip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                clip.close()
                subclip.close()
                return f"Successfully cut video from {start}s to {end}s. Saved to: {output_path}"
                
            elif task == "concatenate":
                if len(input_paths) < 2:
                    return "Error: 'concatenate' requires at least 2 input paths."
                
                clips = []
                for p in input_paths:
                    clips.append(mp.VideoFileClip(p))
                
                final_clip = mp.concatenate_videoclips(clips)
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                
                for c in clips:
                    c.close()
                final_clip.close()
                
                return f"Successfully concatenated {len(input_paths)} videos. Saved to: {output_path}"
                
            elif task == "add_text":
                text = kwargs.get("text", "Text Input Missing")
                filepath = input_paths[0]
                fontsize = kwargs.get("fontsize", 50)
                color = kwargs.get("color", "white")
                
                clip = mp.VideoFileClip(filepath)
                
                # Setup TextClip
                txt_clip = mp.TextClip(text, fontsize=fontsize, color=color)
                
                # Set text duration to match video and place in center
                txt_clip = txt_clip.set_pos('center').set_duration(clip.duration)
                
                video = mp.CompositeVideoClip([clip, txt_clip])
                video.write_videofile(output_path, codec="libx264", audio_codec="aac")
                
                clip.close()
                video.close()
                txt_clip.close()
                
                return f"Successfully added text '{text}' over video. Saved to: {output_path}"
                
            else:
                return f"Error: Unknown task '{task}'. Use cut, concatenate, or add_text."
                
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return f"VideoEditorTool failed with error: {e}\\n{tb}"
