
def render_codebase(codebase: dict, max_chars_per_file: int = 3000) -> str:
    """
    Converts the codebase dict into a readable string for LLM prompts.
    Truncates large files to avoid blowing up the context window.
    
    We truncate at the bottom, not the top.
    The beginning of a file has imports and class definitions,
    important structural information for understanding the codebase.
    """
    lines = ["PROJECT FILES:"]
    
    for filename, content in codebase.items():
        lines.append(f"\n### {filename} ###")
        if len(content) > max_chars_per_file:
            # Keep beginning (imports, class defs)
            lines.append(content[:max_chars_per_file])
            lines.append(f"... [truncated, {len(content)} chars total]")
        else:
            lines.append(content)
    
    return "\n".join(lines)


def render_history(task: str, history: list[dict]) -> str:
    """Compact summary of what has been done so far."""
    lines = [f"TASK: {task}", "\nCOMPLETED STEPS:"]
    
    if not history:
        lines.append("  (none - just started)")
        return "\n".join(lines)
    
    for step in history:
        if step["type"] == "read":
            files = list(step["result"].keys())
            lines.append(f"  READ: Loaded {len(files)} files: {', '.join(files)}")
        
        elif step["type"] == "plan":
            plan = step["result"]
            # Show just the filenames to be changed, not the full plan
            targets = [c["file"] for c in plan.get("changes", [])]
            lines.append(f"  PLAN: Will modify {targets}")
        
        elif step["type"] == "code":
            lines.append(f"  CODE: Patches written for {len(step['result'])} file(s)")
    
    return "\n".join(lines)