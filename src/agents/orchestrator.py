from llm import call_llm_json
from history import render_history


ORCHESTRATOR_SYSTEM_PROMPT = """
You are an orchestrator for a code editing agent.
Read the current state and decide the next step.
Respond ONLY with JSON, no explanation.

Possible actions:
  {"action": "read"}      #no files have been read yet
  {"action": "plan"}      #files are read but no plan exists
  {"action": "code"}      #plan exists but no code has been written
  {"action": "finish"}    #code has been written

Rules:
- Always follow the order: read -> plan -> code -> finish
"""

def orchestrator(task: str, history: list) -> dict:
    context = render_history(task, history)
    return call_llm_json(ORCHESTRATOR_SYSTEM_PROMPT, context)