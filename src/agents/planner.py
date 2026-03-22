"""
The Planner reads the entire codebase
and the user's task, then produces a precise plan in JSON.
"""

from llm import call_llm_json_cached
from history import render_codebase


PLANNER_SYSTEM_PROMPT = """
You are a senior software engineer planning code changes.

You will receive:
1. A user task (bug fix, new feature, or refactor request)
2. The full codebase

Your job is to produce a precise, minimal change plan as JSON.
Respond ONLY with JSON, no explanation, no markdown fences.

The JSON must follow this exact schema:
{
  "reasoning": "Brief explanation of your approach",
  "changes": [
    {
      "file": "relative/path/to/file.py",
      "type": "modify" | "create",
      "description": "Plain English description of what to change in this file",
      "relevant_lines": "e.g. lines 30-45 (the register function)"
    }
  ]
}

Rules:
- Only include files that MUST change, don't touch unrelated files.
- For bug fixes: identify the exact location of the bug first.
- For new features: identify where the feature logically belongs.
- For refactors: identify the specific pattern to improve.
- If a new file must be created, use type "create".
- Keep changes minimal, the smallest change that solves the task.
- Each file must appear only ONCE in the changes list.
- If multiple functions in the same file need changing, describe ALL changes
  for that file in a single "description" field.
- Never duplicate a file in the changes list.
"""

def planner_agent(task: str, codebase: dict) -> dict:
    """
    Reads the codebase and produces a JSON plan.
    
    Returns a dict like:
    {
        "reasoning": "The bug is in file.py line 34...",
        "changes": [
            {
                "file": "file.py",
                "type": "modify",
                "description": "Add bcrypt password hashing to register()",
                "relevant_lines": "lines 30-40"
            }
        ]
    }
    """
    codebase_text = render_codebase(codebase)
    
    user_message = f"""
TASK: {task}

{codebase_text}

Produce your JSON change plan now.
"""
    
    return call_llm_json_cached(PLANNER_SYSTEM_PROMPT, user_message)