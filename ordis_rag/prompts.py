import yaml
import os
from typing import Dict


def load_prompts(file_path="prompts.yaml") -> Dict[str, str]:
    """Loads prompts from a YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")

    with open(file_path, 'r') as f:
        prompts = yaml.safe_load(f)
    return prompts
