# FILE: svcs.py (Updated with Log Filtering)
# This version enhances the `log` command with powerful filtering capabilities,
# similar to `git log`. The separate `search` command has been removed for simplicity.

import argparse
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime
import sys
import os

# Create a robust, absolute path to the .svcs directory
script_dir = os.path.dirname(os.path.realpath(__file__))
svcs_api_path = os.path.join(script_dir, '.svcs')
sys.path.insert(0, svcs_api_path)

try:
    from api import (
        get_full_log, 
        search_events,
        get_valid_commit_hashes,
        prune_orphaned_data
    )
except ImportError as e:
    print(f"Error: Could not import from '.svcs/api.py'. Please ensure the file exists.")
    sys.exit(1)

# --- Helper Functions ---
console = Console()

def display_events(events, title="Semantic Event History"):
    """Renders a list of semantic events in a rich table with metadata."""
    if not events:
        console.print("[bold yellow]No matching semantic events found.[/bold yellow]")
        return

    table = Table(title=title, box=box.MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("Commit", style="yellow", no_wrap=True, width=7)
    table.add_column("Author", style="blue", no_wrap=True, width=15)
    table.add_column("Date", style="dim", no_wrap=True, width=16)
    table.add_column("Event Type", style="cyan", no_wrap=True, width=25)
    table.add_column("Node", style="magenta", no_wrap=True, width=25)
    table.add_column("Location", style="green", no_wrap=True, width=15)
    table.add_column("Details", style="white")

    valid_commits = get_valid_commit_hashes()
    displayed_rows = 0
    for event in events:
        if event["commit_hash"] in valid_commits:
            commit_date = datetime.fromtimestamp(event["timestamp"]).strftime('%Y-%m-%d %H:%M')
            table.add_row(
                event["commit_hash"][:7],
                event["author"],
                commit_date,
                event["event_type"],
                event["node_id"],
                event["location"],
                event["details"]
            )
            displayed_rows += 1
    
    if displayed_rows > 0:
        console.print(table)
    else:
        console.print("[bold yellow]No events found from existing commits.[/bold yellow]")

# --- CLI Command Handlers ---

def handle_log_command(args):
    """
    Handler for the 'log' command. It now handles both displaying the full
    log and displaying a filtered log based on provided arguments.
    """
    try:
        # Check if any filter arguments were provided
        has_filters = any([args.author, args.type, args.node, args.location])
        
        if has_filters:
            # If filters exist, use the search_events API
            events = search_events(
                author=args.author,
                event_type=args.type,
                node_id=args.node,
                location=args.location
            )
            display_events(events, title="Filtered Semantic History")
        else:
            # Otherwise, get the full log
            events = get_full_log()
            display_events(events, title="Semantic Event History")
            
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

def handle_prune_command(args):
    """Handler for the 'prune' command."""
    try:
        console.print("Scanning for orphaned data...")
        pruned_count = prune_orphaned_data()
        if pruned_count > 0:
            console.print(f"[bold green]Success:[/bold green] Pruned data for {pruned_count} orphaned commit(s).")
        else:
            console.print("No orphaned data found. Your semantic history is clean.")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

def main():
    """Main function to parse arguments and run commands."""
    parser = argparse.ArgumentParser(
        description="Semantic VCS (SVCS) - A tool to analyze and query semantic code history."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # log command - NOW WITH FILTERS
    log_parser = subparsers.add_parser("log", help="Display the semantic event log, with optional filters.")
    log_parser.add_argument("-a", "--author", help="Filter by author name.")
    log_parser.add_argument("-t", "--type", help="Filter by event type (e.g., 'dependency_added').")
    log_parser.add_argument("-n", "--node", help="Filter by semantic node (e.g., 'func:greet').")
    log_parser.add_argument("-l", "--location", help="Filter by file location (e.g., 'src/main.py').")
    log_parser.set_defaults(func=handle_log_command)

    # The 'search' command is now removed in favor of enhancing 'log'
    
    # prune command
    prune_parser = subparsers.add_parser(
        "prune",
        help="Remove semantic data for commits no longer in Git history (e.g., from rebase/amend)."
    )
    prune_parser.set_defaults(func=handle_prune_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
