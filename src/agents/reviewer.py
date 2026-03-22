"""
The Validator reviews the patch before it touches real files.
The Validator acts as a code reviewer, it checks if the patch
actually solves the described task, if the old_code actually exists in the file,
and if the new_code looks syntactically correct.
"""

from llm import call_llm_json


LLM_CODE_REVIEWER_PROMPT = """
You are a strict code reviewer.

You will receive:
- A task
- A multi-file diff

Your job:
Determine ONLY whether the changes correctly solve the given task.

You MUST carefully check for:
- missing imports
- undefined functions or variables
- logical correctness
- incomplete implementations
- inconsistencies between files

Important:
- Assume the diff is the ONLY change applied
- Be strict: reject if anything is missing or incorrect
- DO NOT evaluate general code quality
- DO NOT reject for missing features unrelated to the task
- Focus ONLY on whether the specific bug/task was solved

Respond ONLY JSON:

{
  "status": "approved" | "rejected",
  "reason": "short explanation"
}
"""

def reviewer_agent(task: str, diff: str):
    user_message = f"""
TASK:
{task}

CODE DIFF (multi-file):
{diff}

Does this change fully and correctly solve the task?
"""

    return call_llm_json(LLM_CODE_REVIEWER_PROMPT, user_message)