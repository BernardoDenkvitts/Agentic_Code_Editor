"""
Not an LLM agent, just file I/O. Applies approved patches to real files.
"""

import os


def apply_operations(content: str, operations: list) -> str:
    lines = content.splitlines()

    # Apply operations from bottom to top to avoid index shifts affecting subsequent edits
    operations = sorted(operations, key=lambda x: x["start_line"], reverse=True)

    for op in operations:
        t = op["type"]

        if t == "replace":
            start = op["start_line"]
            end = op["end_line"]
            new_lines = op["content"].splitlines()

            lines[start:end+1] = new_lines

        elif t == "delete":
            start = op["start_line"]
            end = op["end_line"]

            del lines[start:end+1]

        elif t == "insert":
            start = op["start_line"]
            new_lines = op["content"].splitlines()

            lines[start:start] = new_lines

        else:
            raise ValueError(f"Unknown operation: {t}")

    return "\n".join(lines) + "\n"


def apply_patch(project_path: str, patch: dict) -> bool:
    full_path = os.path.join(project_path, patch["file"])

    with open(full_path, "r") as f:
        content = f.read()

    try:
        new_content = apply_operations(content, patch["operations"])
    except Exception as e:
        print(f"  Patch failed: {e}")
        return False

    with open(full_path, "w") as f:
        f.write(new_content)

    print(f"  Modified: {patch['file']}")
    return True
