# FILE: .svcs/main.py (Definitive Fix with Corrected Git Interaction)

import subprocess
from rich.console import Console
from rich.table import Table
import sys
import os

# --- Robust Pathing and Imports ---
script_dir = os.path.dirname(os.path.realpath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
from analyzer import analyze_changes
from storage import initialize_database, store_commit_events

console = Console()

def get_parent_hash(commit_hash):
    """Gets the parent hash of a commit, returns None for the initial commit."""
    try:
        # The parent of HEAD is HEAD~1
        return subprocess.check_output(['git', 'rev-parse', f'{commit_hash}~1'], stderr=subprocess.PIPE).decode().strip()
    except subprocess.CalledProcessError:
        # This fails for the very first commit in a repository
        return None

def get_changed_files(commit_hash):
    """
    Uses 'git diff' to get a reliable list of changed files
    between a commit and its parent.
    """
    parent_hash = get_parent_hash(commit_hash)
    if not parent_hash:
        # Initial commit: list all files in the commit
        cmd = ["git", "ls-tree", "-r", "--name-only", commit_hash]
    else:
        # Subsequent commits: find changed files between parent and current
        cmd = ["git", "diff", "--name-only", parent_hash, commit_hash]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = result.stdout.strip().split('\n')
        return [f for f in files if f and (f.endswith(".py") or f.endswith(".php"))]
    except subprocess.CalledProcessError:
        return []

def get_file_content_at_commit(filepath, commit_hash):
    """
    Retrieves the full content of a file at a specific commit hash.
    Returns an empty string if the file doesn't exist at that commit.
    """
    if not commit_hash:
        return ""
    try:
        # Use 'git show' which is the most reliable way to get file content from a specific commit.
        cmd = ["git", "show", f"{commit_hash}:{filepath}"]
        # CORRECTED: Removed the redundant 'stderr=subprocess.PIPE' argument
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        # This is expected if the file was added in this commit (doesn't exist in parent)
        # or deleted in this commit (doesn't exist in current).
        return ""

def get_commit_metadata(commit_hash):
    """Gets metadata for a given commit hash."""
    try:
        author_cmd = ["git", "show", "-s", "--format=%an", commit_hash]
        timestamp_cmd = ["git", "show", "-s", "--format=%ct", commit_hash]
        author = subprocess.check_output(author_cmd).decode().strip()
        timestamp = int(subprocess.check_output(timestamp_cmd).decode().strip())
        return {"author": author, "timestamp": timestamp}
    except subprocess.CalledProcessError:
        return {"author": "N/A", "timestamp": 0}

def run_analysis():
    """Runs the main semantic analysis process."""
    console.print("\n[bold cyan]--=[ SVCS Semantic Analysis ]=--[/bold cyan]")
    commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    parent_hash = get_parent_hash(commit_hash)
    
    console.print(f"[bold magenta][DEBUG][/bold magenta] Analyzing commit: [yellow]{commit_hash[:7]}[/yellow] (Parent: [yellow]{parent_hash[:7] if parent_hash else 'None'}[/yellow])")
    
    changed_files = get_changed_files(commit_hash)
    if not changed_files:
        console.print("No Python files changed in this commit. Nothing to analyze.")
        return

    all_events = []
    for filepath in changed_files:
        console.print(f"[bold magenta][DEBUG][/bold magenta] Processing file: [green]{filepath}[/green]")
        content_before = get_file_content_at_commit(filepath, parent_hash)
        content_after = get_file_content_at_commit(filepath, commit_hash)
        
        # --- Undeniable content debugging ---
        try:
            with open("before.tmp", "w") as f: f.write(content_before)
            with open("after.tmp", "w") as f: f.write(content_after)
            console.print("[bold yellow]DEBUG:[/bold yellow] Wrote file contents to before.tmp and after.tmp")
        except Exception as e:
            console.print(f"[bold red]DEBUG ERROR:[/bold red] Failed to write temp files: {e}")
        
        file_events = analyze_changes(filepath, content_before, content_after)
        all_events.extend(file_events)
    
    if all_events:
        commit_meta = get_commit_metadata(commit_hash)
        db_path = ".svcs/history.db"
        initialize_database(db_path)
        store_commit_events(db_path, commit_hash, commit_meta, all_events)
        console.print(f"\nStored [bold green]{len(all_events)}[/bold green] semantic events in the database.")

    table = Table(title=f"Detected Semantic Events for Commit {commit_hash[:7]}")
    table.add_column("Event Type", style="cyan", no_wrap=True)
    table.add_column("Semantic Node", style="magenta")
    table.add_column("Location", style="green")
    table.add_column("Details", style="yellow")

    if not all_events:
        table.add_row("[yellow]No semantic events detected.[/yellow]", "", "", "")
    else:
        for event in all_events:
            table.add_row(
                event.get("event_type", "N/A"),
                event.get("node_id", "N/A"),
                event.get("location", "N/A"),
                event.get("details", "")
            )
    console.print(table)


if __name__ == "__main__":
    run_analysis()
