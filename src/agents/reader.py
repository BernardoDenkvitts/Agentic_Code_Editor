"""
Reader Agent: Scans a project folder and returns a dict of all Python files.
No LLM is needed. The Reader's job is deterministic, scan files, read content,
return structured data.
"""

import os


ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", "java", "c", "cpp", "cs", "go", "rb", "php",
     "html", "css", "json", ".md", ".txt", ".yaml", ".yml"
}

def reader_agent(project_path: str) -> dict:
    """
    Scans a project folder and returns a dict of all Python files.
    
    Returns:
    {
        "files": {
            "auth.py": "...full file content...",
            "utils.py": "...full file content...",
        }
    }
    """
    files = {}

    for root, dirs, filenames in os.walk(project_path):
        # Skip hidden folders and common non-source folders
        dirs[:] = [d for d in dirs if not d.startswith('.') 
                    and d not in ('__pycache__', 'venv', 'node_modules', '.git')]
        
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue

            full_path = os.path.join(root, filename)
            # Store relative path as key, so agents see "file.py" not "/home/.../file.py"
            relative_path = os.path.relpath(full_path, project_path)

            try:
                with open(full_path, 'r', encoding="utf-8", errors="ignore") as f:
                    files[relative_path] = f.read()
            except Exception:
                # skip unreadable files
                continue
    
    return files