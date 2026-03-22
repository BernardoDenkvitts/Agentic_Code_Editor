"""
Coder Agent: Takes a plan item and writes the code patch.
"""

from llm import call_llm_json_cached


def add_line_numbers(content: str) -> str:
    lines = content.splitlines()
    return "\n".join(f"{i}: {line}" for i, line in enumerate(lines))


CODER_SYSTEM_PROMPT = '''
You are a Senior Software Engineer implementing a code change.

You MUST return edits using line-based operations.

CRITICAL JSON RULES:
- Output MUST be valid JSON parsable by json.loads
- Escape all double quotes as \"
- Use \\n for new lines
- NEVER use triple quotes (""") inside content
- Prefer single quotes (') inside code
- Do not include unescaped characters

You MUST reply in valid JSON format, following the specified rules:

{
  "file": "relative/path/to/file.py",
  "operations": [
    {
      "type": "replace" | "insert" | "delete",
      "start_line": int,
      "end_line": int,        # not required for insert
      "content": "new code"
    }
  ],
  "explanation": "one sentence explaining the change"
}

Rules:
- Lines are 0-indexed
- end_line is inclusive
- replace: replaces lines [start_line, end_line]
- delete: removes lines [start_line, end_line]
- insert: inserts content at start_line
- content must be valid code
- DO NOT include old_code
- The final file must be runnable and self-contained
- Remember to include necessary imports if the new modification requires them
- Do NOT assume functions already exist unless they are present in the file
- The "content" field MUST include the exact leading whitespace (spaces/indentation) required to match the file's structure
'''

def coder_agent(plan_item: dict, file_content: str) -> dict:
    """
    Takes one item from the Planner's plan and writes the patch.
    
    plan_item: one entry from plan["changes"]
    file_content: the current content of the file to modify
    
    Returns a patch dict: {file, old_code, new_code, explanation}
    """
    numbered_content = add_line_numbers(file_content)

    user_message = f"""
CHANGE TO IMPLEMENT:
File: {plan_item['file']}
Type: {plan_item['type']}
Description: {plan_item['description']}
Relevant area: {plan_item.get('relevant_lines', 'not specified')}

CURRENT FILE CONTENT (with line numbers):
{numbered_content}

Produce your patch now. Strictly in **VALID JSON** format.
"""
    
    return call_llm_json_cached(CODER_SYSTEM_PROMPT, user_message)