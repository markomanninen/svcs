#!/usr/bin/env python3
"""
SVCS CLI - Unified Command Line Interface
Repository-Local Semantic Version Control System

Complete command set:
  svcs init         - Initialize SVCS in current repository
  svcs init-project - Interactive tour to setup a new SVCS project
  svcs status       - Show SVCS status  
  svcs events       - List recent semantic events
  svcs search       - Advanced semantic search
  svcs evolution    - Track function/class evolution
  svcs analytics    - Generate analytics reports
  svcs quality      - Quality analysis
  svcs dashboard    - Generate static dashboard
  svcs web          - Interactive web dashboard
  svcs ci           - CI/CD integration
  svcs discuss      - Conversational interface
  svcs query        - Natural language queries
  svcs notes        - Git notes management
  svcs compare      - Compare branches
  svcs cleanup      - Repository maintenance
  svcs mcp          - MCP server management
"""

import sys
from pathlib import Path
# Ensure package root is on sys.path for console_scripts entry points
package_root = Path(__file__).parent.parent
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import threading
import time

# Try to import from installed package, fallback to parent directory
try:
    from svcs_repo_local import RepositoryLocalSVCS, SVCSMigrator
    from svcs_repo_hooks import SVCSRepositoryManager
    from .commands import *  # Import all commands from modular package
    from .commands.init import cmd_init_project # Ensure cmd_init_project is imported
except ImportError:
    # Fallback to parent directory (development mode)
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    try:
        from svcs_repo_local import RepositoryLocalSVCS, SVCSMigrator
        from svcs_repo_hooks import SVCSRepositoryManager
        # Import modular commands in development mode
        sys.path.insert(0, str(Path(__file__).parent))
        from commands import *
        from commands.init import cmd_init_project
    except ImportError:
        print("❌ Error: SVCS modules not found. Please ensure SVCS is properly installed.")
        print(f"   Searched in: {Path(__file__).parent} and {parent_dir}")
        sys.exit(1)

# Import utilities
try:
    from . import utils
except ImportError:
    # Development mode fallback
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    try:
        import utils
    except ImportError:
        print("❌ Warning: Utils module not found.")
        utils = None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SVCS - Semantic Version Control System (Repository-Local)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Complete command set:
  svcs init                           # Initialize SVCS in current repository
  svcs init-project [name] [--path .] [--non-interactive] # Interactive tour / setup for new project
  svcs status                         # Show repository status
  svcs events                         # List recent semantic events
  svcs search "query"                 # Advanced semantic search
  svcs evolution "func:name"          # Track function evolution
  svcs analytics                      # Generate analytics reports  
  svcs quality                        # Quality analysis
  svcs dashboard                      # Generate static dashboard
  svcs web start                      # Start interactive web dashboard
  svcs ci pr-analysis                 # CI/CD integration
  svcs discuss                        # Conversational interface
  svcs discuss --query "summary"      # Start with initial query
  svcs query "natural language"       # One-shot natural language queries
  svcs notes sync                     # Git notes team collaboration
  svcs compare main feature           # Compare branches
  svcs cleanup                        # Repository maintenance
  svcs mcp start                     # Start MCP server

Examples:
  svcs init                           # Initialize current repository
  svcs events --limit 50              # Show 50 recent events
  svcs search --pattern-type performance --confidence 0.8
  svcs search --event-type "signature_change" --author john
  svcs search --since "1 week ago" --location "src/"
  svcs evolution "func:process_data"  # Track function evolution
  svcs analytics --output report.json --format json
  svcs quality --verbose              # Detailed quality analysis
  svcs web start --port 9000          # Start dashboard on port 9000
  svcs discuss                        # Start interactive conversation
  svcs discuss --query "summarize recent changes"  # Start with initial query
  svcs query "show me performance optimizations"   # One-shot query
  svcs compare main develop           # Compare semantic patterns

Search Pattern Types (--pattern-type):
  performance          # Performance optimizations and bottlenecks
  architecture         # Architectural patterns and design changes  
  error_handling       # Exception handling and error patterns
  refactoring          # Code refactoring patterns
  
Common Event Types (--event-type):
  signature_change     # Function/method signature changes
  behavior_change      # Behavioral modifications
  performance_optimization  # Performance improvements
  dependency_addition  # New dependencies added
  error_handling_improvement  # Better error handling
  
Date Formats (--since):
  "2024-01-01"        # Specific date (YYYY-MM-DD)
  "1 week ago"        # Relative time
  "2 months ago"      # Relative time
  "yesterday"         # Relative time
        """
    )
    
    parser.add_argument('--path', '-p', type=str,
                       help='Repository path (default: current directory)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize SVCS for repository (auto-detects git)')
    init_parser.set_defaults(func=cmd_init)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show SVCS status')
    status_parser.set_defaults(func=cmd_status)
    
    # Events command
    events_parser = subparsers.add_parser('events', help='List semantic events')
    events_parser.add_argument('--limit', '-l', type=int, default=20,
                              help='Maximum number of events to show')
    events_parser.add_argument('--branch', '-b', type=str,
                              help='Branch to query (default: current)')
    events_parser.add_argument('--type', '-t', type=str,
                              help='Filter by event type')
    events_parser.set_defaults(func=cmd_events)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Advanced semantic search')
    search_parser.add_argument('--pattern-type', type=str,
                              help='Search for specific patterns (performance, architecture, etc.)')
    search_parser.add_argument('--event-type', type=str,
                              help='Filter by event type')
    search_parser.add_argument('--author', type=str,
                              help='Filter by author')
    search_parser.add_argument('--since', type=str,
                              help='Events since date (e.g., "2024-01-01", "1 week ago")')
    search_parser.add_argument('--confidence', type=float, default=0.0,
                              help='Minimum confidence threshold (0.0-1.0)')
    search_parser.add_argument('--location', type=str,
                              help='Filter by file/location pattern')
    search_parser.add_argument('--limit', '-l', type=int, default=20,
                              help='Maximum number of results')
    search_parser.set_defaults(func=cmd_search)
    
    # Evolution command
    evolution_parser = subparsers.add_parser('evolution', help='Track function/class evolution')
    evolution_parser.add_argument('node_id', help='Node ID to track (e.g., "func:process_data")')
    evolution_parser.add_argument('--event-types', nargs='*',
                                 help='Filter by specific event types')
    evolution_parser.add_argument('--confidence', type=float, default=0.0,
                                 help='Minimum confidence threshold')
    evolution_parser.add_argument('--since', type=str,
                                 help='Events since date')
    evolution_parser.set_defaults(func=cmd_evolution)
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Generate analytics reports')
    analytics_parser.add_argument('--output', '-o', type=str,
                                 help='Output file path')
    analytics_parser.add_argument('--format', choices=['json'], default='json',
                                 help='Output format')
    analytics_parser.add_argument('--branch', '-b', type=str,
                                 help='Analyze specific branch')
    analytics_parser.set_defaults(func=cmd_analytics)
    
    # Quality command
    quality_parser = subparsers.add_parser('quality', help='Quality analysis')
    quality_parser.add_argument('--output', '-o', type=str,
                               help='Output file path')
    quality_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Verbose output')
    quality_parser.set_defaults(func=cmd_quality)
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Generate static dashboard')
    dashboard_parser.add_argument('--output', '-o', type=str,
                                 help='Output HTML file path')
    dashboard_parser.add_argument('--theme', choices=['light', 'dark'], default='light',
                                 help='Dashboard theme')
    dashboard_parser.set_defaults(func=cmd_dashboard)
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Interactive web dashboard')
    web_parser.add_argument('action', choices=['start', 'stop', 'status'],
                           help='Web server action')
    web_parser.add_argument('--host', default='127.0.0.1',
                           help='Host to bind to')
    web_parser.add_argument('--port', '-p', type=int, default=8080,
                           help='Port to bind to')
    web_parser.add_argument('--debug', action='store_true',
                           help='Enable debug mode')
    web_parser.add_argument('--background', action='store_true',
                           help='Run in background')
    web_parser.set_defaults(func=cmd_web)
    
    # CI command
    ci_parser = subparsers.add_parser('ci', help='CI/CD integration')
    ci_parser.add_argument('ci_command', choices=['pr-analysis', 'quality-gate', 'report'],
                          help='CI command to run')
    ci_parser.add_argument('--target', type=str,
                          help='Target branch for PR analysis')
    ci_parser.add_argument('--strict', action='store_true',
                          help='Strict quality gate mode')
    ci_parser.add_argument('--format', choices=['text', 'json', 'junit'],
                          help='Report format')
    ci_parser.set_defaults(func=cmd_ci)
    
    # Discuss command
    discuss_parser = subparsers.add_parser('discuss', help='Conversational interface')
    discuss_parser.add_argument('--query', '-q', type=str,
                               help='Initial query to start conversation with')
    discuss_parser.set_defaults(func=cmd_discuss)
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Natural language query')
    query_parser.add_argument('query', help='Natural language query string')
    query_parser.set_defaults(func=cmd_query)
    
    # Notes command
    notes_parser = subparsers.add_parser('notes', help='Git notes management')
    notes_parser.add_argument('notes_action', choices=['sync', 'fetch', 'show', 'status'],
                             help='Notes action')
    notes_parser.add_argument('--commit', type=str,
                             help='Commit hash for show action')
    notes_parser.set_defaults(func=cmd_notes)
    
    # Compare command  
    compare_parser = subparsers.add_parser('compare', help='Compare branches')
    compare_parser.add_argument('branch1', help='First branch to compare')
    compare_parser.add_argument('branch2', help='Second branch to compare')
    compare_parser.add_argument('--limit', '-l', type=int, default=10,
                               help='Maximum events per branch to show')
    compare_parser.set_defaults(func=cmd_compare)
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Repository maintenance')
    cleanup_parser.add_argument('--git-unreachable', action='store_true',
                               help='Clean events for unreachable commits')
    cleanup_parser.add_argument('--show-stats', action='store_true',
                               help='Show database statistics')
    cleanup_parser.set_defaults(func=cmd_cleanup)
    
    # Configuration command
    config_parser = subparsers.add_parser('config', help='Configure SVCS settings')
    config_subparsers = config_parser.add_subparsers(dest="config_action", required=True)
    
    # Config set
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('setting', help='Setting name (e.g., auto-sync)')
    config_set_parser.add_argument('value', help='Setting value')
    
    # Config get
    config_get_parser = config_subparsers.add_parser('get', help='Get configuration value')
    config_get_parser.add_argument('setting', nargs='?', help='Setting name (optional)')
    
    # Config list
    config_list_parser = config_subparsers.add_parser('list', help='List all configuration')
    
    config_parser.set_defaults(func=cmd_config)
    
    # Process-hook command (for git hooks)
    hook_parser = subparsers.add_parser('process-hook', help='Process git hook (internal use)')
    hook_parser.add_argument('hook_name', help='Git hook name (e.g., post-commit)')
    hook_parser.add_argument('hook_args', nargs='*', help='Hook arguments')
    hook_parser.set_defaults(func=cmd_process_hook)
    
    # Add process-merge subcommand
    process_merge_parser = events_parser.add_subparsers(dest="events_command").add_parser("process-merge", help="Process semantic event merge")
    process_merge_parser.add_argument("--source-branch", default=None, help="Source branch (optional)")
    process_merge_parser.add_argument("--target-branch", default=None, help="Target branch (optional)")
    
    # Streamlined workflow commands
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Enhanced git pull with semantic event sync')
    pull_parser.add_argument('--path', '-p', type=str, help='Repository path')
    pull_parser.set_defaults(func=cmd_pull)
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Enhanced git push with semantic notes sync')
    push_parser.add_argument('--path', '-p', type=str, help='Repository path')
    push_parser.add_argument('remote', nargs='?', help='Remote name (optional)')
    push_parser.add_argument('branch', nargs='?', help='Branch name (optional)')
    push_parser.set_defaults(func=cmd_push)
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Enhanced git merge with semantic event transfer')
    merge_parser.add_argument('branch', help='Branch to merge')
    merge_parser.add_argument('--path', '-p', type=str, help='Repository path')
    merge_parser.add_argument('--no-ff', action='store_true', help='Create merge commit even for fast-forward')
    merge_parser.add_argument('--message', '-m', type=str, help='Merge commit message')
    merge_parser.add_argument('--manual-transfer', action='store_true', help='Manually trigger semantic event transfer')
    merge_parser.set_defaults(func=cmd_merge)
    
    # Sync command for simplified remote semantic data sync
    sync_parser = subparsers.add_parser('sync', help='Sync semantic data with remote')
    sync_parser.set_defaults(func=cmd_sync)
    
    # Complete sync command for complex scenarios
    sync_all_parser = subparsers.add_parser('sync-all', help='Complete sync after git operations')
    sync_all_parser.set_defaults(func=cmd_sync_all)
    
    # Merge resolve command for post-merge semantic event issues
    merge_resolve_parser = subparsers.add_parser('merge-resolve', help='Resolve post-merge semantic issues')
    merge_resolve_parser.set_defaults(func=cmd_merge_resolve)
    
    # Auto-fix command for common issues
    auto_fix_parser = subparsers.add_parser('auto-fix', help='Auto-detect and fix common SVCS issues')
    auto_fix_parser.set_defaults(func=cmd_auto_fix)
    
    # Quick help command
    quick_help_parser = subparsers.add_parser('help', help='Quick workflow help and cheat sheet')
    quick_help_parser.set_defaults(func=cmd_quick_help)
    
    # Workflow guide command
    workflow_parser = subparsers.add_parser('workflow', help='Show SVCS workflow guide')
    workflow_parser.add_argument('--type', choices=['basic', 'team', 'troubleshooting'], 
                                default='basic', help='Type of workflow guide')
    workflow_parser.set_defaults(func=cmd_workflow)
    
    # MCP Server commands
    mcp_parser = subparsers.add_parser('mcp', help='MCP server management')
    mcp_subparsers = mcp_parser.add_subparsers(dest='mcp_command', help='MCP server operations')
    
    # MCP start command
    mcp_start_parser = mcp_subparsers.add_parser('start', help='Start MCP server for IDE integration')
    mcp_start_parser.add_argument('--background', '-b', action='store_true', 
                                 help='Run server in background')
    mcp_start_parser.add_argument('--log-file', type=str, 
                                 help='Log file path (default: ~/Library/Logs/Claude/mcp-server-svcs.log)')
    mcp_start_parser.set_defaults(func=cmd_mcp_start)
    
    # MCP stop command
    mcp_stop_parser = mcp_subparsers.add_parser('stop', help='Stop MCP server')
    mcp_stop_parser.set_defaults(func=cmd_mcp_stop)
    
    # MCP status command
    mcp_status_parser = mcp_subparsers.add_parser('status', help='Check MCP server status')
    mcp_status_parser.set_defaults(func=cmd_mcp_status)
    
    # MCP restart command
    mcp_restart_parser = mcp_subparsers.add_parser('restart', help='Restart MCP server')
    mcp_restart_parser.add_argument('--background', '-b', action='store_true', 
                                   help='Run server in background')
    mcp_restart_parser.set_defaults(func=cmd_mcp_restart)
    
    # MCP logs command
    mcp_logs_parser = mcp_subparsers.add_parser('logs', help='Show MCP server logs')
    mcp_logs_parser.add_argument('--lines', '-n', type=int, default=50,
                                help='Number of log lines to show')
    mcp_logs_parser.add_argument('--follow', '-f', action='store_true',
                                help='Follow log output')
    mcp_logs_parser.set_defaults(func=cmd_mcp_logs)

    # Init-project command
    init_project_parser = subparsers.add_parser('init-project', help='Initialize a new SVCS project with an interactive tour or non-interactively.')
    init_project_parser.add_argument('project_name', nargs='?', default=None, help='Name of the new project (optional, will be prompted if not provided in interactive mode, or uses a default in non-interactive mode if not set)')
    init_project_parser.add_argument('--path', type=str, help='Directory to create the project in (default: current directory if interactive, or prompted)')
    init_project_parser.add_argument('--non-interactive', action='store_true', help='Run in non-interactive mode, using defaults and skipping prompts.')
    init_project_parser.set_defaults(func=cmd_init_project)

    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    try:
        args.func(args)
        if args.command == "events" and hasattr(args, "events_command"):
            repo_path = args.path or '.'
            svcs = RepositoryLocalSVCS(repo_path)
            if args.events_command == "process-merge":
                result = svcs.process_merge(
                    source_branch=args.source_branch,
                    target_branch=args.target_branch
                )
                print(result)
                return
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
