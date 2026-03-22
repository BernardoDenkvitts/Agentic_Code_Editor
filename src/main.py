import difflib
import argparse
from enum import Enum
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax

from agents.reader import reader_agent
from agents.orchestrator import orchestrator
from agents.planner import planner_agent
from agents.coder import coder_agent
from agents.reviewer import reviewer_agent
from patcher import apply_patch, apply_operations

console = Console()

class AgentAction(str, Enum):
    READ = "read"
    PLAN = "plan"
    CODE = "code"
    FINISH = "finish"

def generate_diff(original: str, modified: str) -> str:
    return "\n".join(difflib.unified_diff(
        original.splitlines(),
        modified.splitlines(),
        lineterm=""
    ))

def _handle_read(project_path: str, target_files: Optional[List[str]], history: List[Dict[str, Any]]) -> Dict[str, str]:
    console.print("  [dim]Reading codebase...[/dim]")
    codebase = reader_agent(project_path)

    if target_files:
        filtered = {
            f: c for f, c in codebase.items()
            if f in target_files
        }
        if not filtered:
            console.print("\n  [yellow]Warning: No files matched your filter. Using full codebase.[/yellow]\n")
        else:
            codebase = filtered

    history.append({"type": "read", "result": codebase})
    console.print(f"  [dim]Loaded: {list(codebase.keys())}[/dim]")
    return codebase

def _handle_plan(task: str, codebase: Dict[str, str], history: List[Dict[str, Any]]) -> Dict[str, Any]:
    console.print("  [dim]Planning changes...[/dim]")
    plan = planner_agent(task, codebase)
    history.append({"type": "plan", "result": plan})
    console.print(f"  [dim]Will touch: {[c['file'] for c in plan['changes']]}[/dim]")
    return plan

def _handle_code(plan: Dict[str, Any], codebase: Dict[str, str], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    console.print("  [dim]Writing code...[/dim]")
    patches = []

    for change in plan["changes"]:
        file_content = codebase.get(change["file"], "")
        patch = coder_agent(change, file_content)
        patches.append(patch)
    
    history.append({"type": "code", "result": patches})
    return patches

def _handle_finish(task: str, project_path: str, codebase: Dict[str, str], plan: Dict[str, Any], patches: List[Dict[str, Any]]) -> bool:
    console.print("\n  [bold green]Proposed changes:[/bold green]\n")

    all_diffs_text = ""

    for patch in patches:
        file_name = patch["file"]
        
        original = codebase.get(file_name, "")
        modified = apply_operations(original, patch["operations"])

        diff = generate_diff(original, modified)

        console.print(f"\n[bold cyan]=== {file_name} ===[/bold cyan]")
        syntax = Syntax(diff, "diff", theme="monokai", line_numbers=False)
        console.print(syntax)
        console.print()

        all_diffs_text += f"\n=== FILE: {file_name} ===\n"
        all_diffs_text += diff + "\n"

    use_llm_review = Confirm.ask("\n  Ask Reviewer Agent to review these changes?")
    if use_llm_review:
        console.print("\n  [dim]Reviewing all changes together...[/dim]")
        review = reviewer_agent(task, all_diffs_text)
        
        status_color = "green" if review['status'].lower() == "approved" else "red"
        console.print(f"\n  Reviewer Agent verdict: [bold {status_color}]{review['status']}[/bold {status_color}]")
        console.print(f"  Reason: {review['reason']}\n")

    confirm = Confirm.ask("\n  Apply these changes?")

    if not confirm:
        console.print("  [yellow]Changes rejected by user.[/yellow]")
        return False

    console.print("\n  [dim]Applying patches to files...[/dim]")
    for patch in patches:
        apply_patch(project_path, patch)
    
    console.print("\n  [bold green]Done![/bold green]")
    return True

def run(project_path: str, task: str, target_files: Optional[List[str]] = None):
    console.print()
    console.print(Panel(
        f"[bold cyan]Task:[/bold cyan] {task}", 
        title=f"Project: {project_path}",
        border_style="blue"
    ))
    
    history: List[Dict[str, Any]] = []
    codebase: Dict[str, str] = {}
    plan: Optional[Dict[str, Any]] = None
    patches: List[Dict[str, Any]] = []

    while True:
        action_dict = orchestrator(task, history)
        
        try:
            action = AgentAction(action_dict["action"])
        except ValueError:
            console.print(f"  [bold red]Unknown action:[/bold red] {action_dict}. Stopping.")
            break

        console.print(f"\n  [bold magenta]Orchestrator:[/bold magenta] {action.value}")

        if action == AgentAction.READ:
            codebase = _handle_read(project_path, target_files, history)
            if not codebase:
                console.print("  [red]No files found. Stopping.[/red]")
                break

        elif action == AgentAction.PLAN:
            if not codebase:
                console.print("  [red]Codebase not loaded. Cannot plan.[/red]")
                break
            plan = _handle_plan(task, codebase, history)

        elif action == AgentAction.CODE:
            if not plan:
                console.print("  [red]Plan not created. Cannot write code.[/red]")
                break

            patches = _handle_code(plan, codebase, history)

        elif action == AgentAction.FINISH:
            if not patches:
                console.print("  [red]No patches generated to finish.[/red]")
                break
                
            finished = _handle_finish(task, project_path, codebase, plan, patches)
            if not finished:
                break
            return

def main():
    parser = argparse.ArgumentParser(description="Agent Orchestrator")
    parser.add_argument("--project", "-p", type=str, default="../sample_project", help="Path to the project folder")
    parser.add_argument("--task", "-t", type=str, default="Fix the bug where passwords are stored in plain text", help="The task for the agent to execute")
    parser.add_argument("--files", "-f", type=str, nargs="*", default=None, help="(Optional) Specific files to target")

    args = parser.parse_args()

    if args.files:
        clean_files = []
        for f in args.files:
            clean_files.extend([x.strip() for x in f.split(",") if x.strip()])
        args.files = clean_files

    run(args.project, args.task, args.files)

if __name__ == "__main__":
    main()