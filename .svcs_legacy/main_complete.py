# FILE: .svcs/main_complete.py (Complete 5-Layer Integration)

import subprocess
from rich.console import Console
from rich.table import Table
import sys
import os

# --- Robust Pathing and Imports ---
script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(script_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from storage import initialize_database, store_commit_events

# Import LLM logger
try:
    from llm_logger import llm_logger
except ImportError:
    llm_logger = None

# Import the complete 5-layer analyzer
try:
    from svcs_complete_5layer import SVCSComplete5LayerAnalyzer
    COMPLETE_ANALYZER_AVAILABLE = True
except ImportError:
    # Fallback to original analyzer
    from analyzer import analyze_changes
    COMPLETE_ANALYZER_AVAILABLE = False

console = Console()

def get_parent_hash(commit_hash):
    """Gets the parent hash of a commit, returns None for the initial commit."""
    try:
        return subprocess.check_output(['git', 'rev-parse', f'{commit_hash}~1'], stderr=subprocess.PIPE).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_changed_files(commit_hash):
    """Uses 'git diff' to get a reliable list of changed files."""
    parent_hash = get_parent_hash(commit_hash)
    if not parent_hash:
        cmd = ["git", "ls-tree", "-r", "--name-only", commit_hash]
    else:
        cmd = ["git", "diff", "--name-only", parent_hash, commit_hash]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = result.stdout.strip().split('\n')
        return [f for f in files if f and (f.endswith(".py") or f.endswith(".php"))]
    except subprocess.CalledProcessError:
        return []

def get_file_content_at_commit(filepath, commit_hash):
    """Retrieves the full content of a file at a specific commit hash."""
    if not commit_hash:
        return ""
    try:
        cmd = ["git", "show", f"{commit_hash}:{filepath}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
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

def run_complete_analysis():
    """Runs the complete 5-layer semantic analysis process."""
    console.print("\n[bold cyan]🚀 SVCS COMPLETE 5-LAYER SEMANTIC ANALYSIS 🚀[/bold cyan]")
    
    # Show analyzer status
    if COMPLETE_ANALYZER_AVAILABLE:
        console.print("[bold green]✅ Complete 5-Layer Analyzer Available[/bold green]")
        analyzer = SVCSComplete5LayerAnalyzer()
        layer_status = analyzer.get_layer_status()
        
        console.print("[bold yellow]📊 Layer Status:[/bold yellow]")
        status_info = [
            ("Core (1-4)", layer_status.get('core', False), "Structural & Syntactic"),
            ("Layer 5a", layer_status.get('layer5_ai', False), "AI Pattern Recognition"), 
            ("Layer 5b", layer_status.get('layer5_true_ai', False), "True AI Abstract Analysis"),
            ("Multi-lang", layer_status.get('multilang', False), "Multi-language Support")
        ]
        
        for layer_name, available, description in status_info:
            status = "✅" if available else "❌"
            console.print(f"   {status} {layer_name}: {description}")
    else:
        console.print("[bold yellow]⚠️ Fallback to Original Analyzer[/bold yellow]")
    
    commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    parent_hash = get_parent_hash(commit_hash)
    
    console.print(f"[bold magenta]🔍 Analyzing commit:[/bold magenta] [yellow]{commit_hash[:7]}[/yellow] (Parent: [yellow]{parent_hash[:7] if parent_hash else 'None'}[/yellow])")
    
    changed_files = get_changed_files(commit_hash)
    if not changed_files:
        console.print("No Python/PHP files changed in this commit. Nothing to analyze.")
        return

    all_events = []
    for filepath in changed_files:
        console.print(f"[bold magenta]📁 Processing file:[/bold magenta] [green]{filepath}[/green]")
        content_before = get_file_content_at_commit(filepath, parent_hash)
        content_after = get_file_content_at_commit(filepath, commit_hash)
        
        # Debug file contents
        try:
            with open("before.tmp", "w") as f: f.write(content_before)
            with open("after.tmp", "w") as f: f.write(content_after)
            console.print("[bold yellow]📝 DEBUG:[/bold yellow] Wrote file contents to before.tmp and after.tmp")
        except Exception as e:
            console.print(f"[bold red]DEBUG ERROR:[/bold red] Failed to write temp files: {e}")
        
        # Run analysis with logging
        if COMPLETE_ANALYZER_AVAILABLE:
            # If analyzer uses LLM, wrap it with logging
            try:
                file_events = analyzer.analyze_complete(filepath, content_before, content_after)
                
                # Log if any LLM calls were made during analysis
                if llm_logger and hasattr(analyzer, '_last_llm_calls'):
                    for call in analyzer._last_llm_calls:
                        llm_logger.log_inference(
                            component="layer5_analysis",
                            prompt=call.get('prompt', ''),
                            response=call.get('response', ''),
                            model=call.get('model', 'unknown'),
                            metadata={
                                'filepath': filepath,
                                'commit_hash': commit_hash[:7],
                                'analysis_layer': call.get('layer', 'unknown')
                            }
                        )
                        
            except Exception as e:
                if llm_logger:
                    llm_logger.log_error(
                        component="layer5_analysis",
                        prompt=f"Analysis of {filepath}",
                        error=str(e),
                        model="unknown",
                        metadata={'filepath': filepath, 'commit_hash': commit_hash[:7]}
                    )
                raise
        else:
            # Fallback to original analyzer
            file_events = analyze_changes(filepath, content_before, content_after)
        
        all_events.extend(file_events)
    
    # Store results
    if all_events:
        commit_meta = get_commit_metadata(commit_hash)
        db_path = ".svcs/history.db"
        initialize_database(db_path)
        store_commit_events(db_path, commit_hash, commit_meta, all_events)
        console.print(f"\n[bold green]💾 Stored {len(all_events)} semantic events in database[/bold green]")

    # Display results
    if COMPLETE_ANALYZER_AVAILABLE and all_events:
        # Group events by layer for display
        by_layer = {}
        for event in all_events:
            layer = event.get('layer', 'unknown')
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(event)
        
        console.print(f"\n[bold cyan]📊 ANALYSIS SUMMARY[/bold cyan]")
        for layer, events in sorted(by_layer.items()):
            console.print(f"   [bold magenta]{layer.upper()}:[/bold magenta] {len(events)} events")
    
    # Traditional table view
    table = Table(title=f"Semantic Events for Commit {commit_hash[:7]}")
    table.add_column("Layer", style="blue", no_wrap=True)
    table.add_column("Event Type", style="cyan", no_wrap=True)
    table.add_column("Node", style="magenta")
    table.add_column("Location", style="green")
    table.add_column("Details", style="yellow")

    if not all_events:
        table.add_row("", "[yellow]No semantic events detected.[/yellow]", "", "", "")
    else:
        for event in all_events:
            layer = event.get("layer", "?")
            table.add_row(
                layer,
                event.get("event_type", "N/A"),
                event.get("node_id", "N/A"),
                event.get("location", "N/A"),
                event.get("details", "")[:100] + "..." if len(event.get("details", "")) > 100 else event.get("details", "")
            )
    
    console.print(table)
    console.print(f"\n[bold green]🎉 5-Layer Analysis Complete! Total Events: {len(all_events)}[/bold green]")


if __name__ == "__main__":
    run_complete_analysis()
