import json
import os

def load_prompts(file_path="prompts/prompts.json"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found at {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)
    return prompts

