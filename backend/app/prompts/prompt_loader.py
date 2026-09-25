"""
prompt_loader.py

Purpose:
    Utility module to load and cache markdown/text prompt templates
    from the app/prompts directory.

Input:
    Prompt file name (e.g. "planner.md", "writer.md", "auditor.md").

Output:
    Raw prompt template string with variable placeholders.
"""

from pathlib import Path
from functools import lru_cache

PROMPTS_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=32)
def load_prompt(filename: str) -> str:
    """Loads a prompt markdown template from app/prompts."""
    file_path = PROMPTS_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt template '{filename}' not found at {file_path}")
    return file_path.read_text(encoding="utf-8")
