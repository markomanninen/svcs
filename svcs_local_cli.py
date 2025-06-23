#!/usr/bin/env python3
"""
Repository-Local SVCS CLI Tool

New command-line interface for the git-integrated team architecture:
- Repository-local semantic storage
- Git notes integration for team collaboration
- Branch-aware semantic analysis
- Migration tools from global architecture
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from svcs_repo_local import RepositoryLocalSVCS, SVCSMigrator
from svcs_repo_hooks import SVCSRepositoryManager


def cmd_init(args):
    """Initialize SVCS for current repository."""
    manager = SVCSRepositoryManager(args.path)
    result = manager.setup_repository()
    print(result)


def cmd_status(args):
    """Show SVCS status for current repository."""
    svcs = RepositoryLocalSVCS(args.path or Path.cwd())
    status = svcs.get_repository_status()
    
    if not status["initialized"]:
        print(f"❌ SVCS not initialized for repository: {args.path or Path.cwd()}")
        print("Run 'svcs-local init' to initialize SVCS for this repository.")
        return
    
    print(f"✅ SVCS Repository Status")
    print(f"📁 Repository: {status['repository_path']}")
    print(f"🌿 Current branch: {status['current_branch']}")
    print(f"🔢 Semantic events: {status['semantic_events_count']}")
    print(f"📝 Commits analyzed: {status['commits_analyzed']}")
    print(f"📅 Initialized: {datetime.fromtimestamp(status['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_events(args):
    """List semantic events for current branch."""
    svcs = RepositoryLocalSVCS(args.path or Path.cwd())
    
    if not svcs.db.db_path.exists():
        print("❌ SVCS not initialized for this repository")
        return
    
    events = svcs.db.get_branch_events(args.branch, args.limit)
    
    if not events:
        branch_name = args.branch or svcs.db.get_current_branch()
        print(f"ℹ️ No semantic events found for branch: {branch_name}")
        return
    
    print(f"📊 Semantic Events ({len(events)} found)")
    print("=" * 60)
    
    for event in events:
        timestamp = datetime.fromtimestamp(event['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        confidence = f" ({event['confidence']:.1%})" if event['confidence'] != 1.0 else ""
        
        print(f"🔍 {event['event_type']}{confidence}")
        print(f"   📝 {event['commit_hash'][:8]} | {event['branch']} | {timestamp}")
        print(f"   🎯 {event['node_id']} @ {event['location']}")
        print(f"   💬 {event['details']}")
        if event['reasoning']:
            print(f"   🧠 {event['reasoning']}")
        print()


def cmd_notes(args):
    """Manage git notes for semantic data."""
    svcs = RepositoryLocalSVCS(args.path or Path.cwd())
    
    if args.action == "sync":
        success = svcs.git_notes.sync_notes_to_remote(args.remote)
        if success:
            print(f"✅ Semantic git notes synced to {args.remote}")
        else:
            print(f"❌ Failed to sync git notes to {args.remote}")
    
    elif args.action == "fetch":
        success = svcs.git_notes.fetch_notes_from_remote(args.remote)
        if success:
            print(f"✅ Semantic git notes fetched from {args.remote}")
        else:
            print(f"⚠️ No semantic git notes found on {args.remote}")
    
    elif args.action == "show":
        commit_hash = args.commit
        if not commit_hash:
            # Get latest commit
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=svcs.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                commit_hash = result.stdout.strip()
            else:
                print("❌ Could not determine current commit")
                return
        
        semantic_data = svcs.git_notes.get_semantic_data_from_note(commit_hash)
        if semantic_data:
            print(f"📝 Semantic git note for commit {commit_hash[:8]}:")
            print(json.dumps(semantic_data, indent=2))
        else:
            print(f"ℹ️ No semantic git note found for commit {commit_hash[:8]}")


def cmd_migrate(args):
    """Migrate from global to repository-local SVCS."""
    migrator = SVCSMigrator(args.global_db)
    
    if args.action == "list":
        projects = migrator.list_migratable_projects()
        if not projects:
            print("ℹ️ No projects found in global database")
            return
        
        print("📋 Projects available for migration:")
        print("=" * 50)
        for project in projects:
            print(f"📁 {project['name']}")
            print(f"   📂 Path: {project['path']}")
            print(f"   🔢 Events: {project['event_count']}")
            print(f"   📅 Created: {datetime.fromtimestamp(project['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    elif args.action == "migrate":
        project_path = args.project_path or Path.cwd()
        result = migrator.migrate_project_to_local(project_path)
        print(result)


def cmd_remove(args):
    """Remove SVCS from current repository."""
    if not args.force:
        response = input("Are you sure you want to remove SVCS from this repository? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled")
            return
    
    manager = SVCSRepositoryManager(args.path)
    result = manager.teardown_repository()
    print(result)


def cmd_analyze(args):
    """Manually analyze a specific commit."""
    from svcs_repo_analyzer import RepositoryLocalSemanticAnalyzer
    
    svcs = RepositoryLocalSVCS(args.path or Path.cwd())
    analyzer = RepositoryLocalSemanticAnalyzer(args.path or Path.cwd())
    
    commit_hash = args.commit
    if not commit_hash:
        # Get latest commit
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=svcs.repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            commit_hash = result.stdout.strip()
        else:
            print("❌ Could not determine current commit")
            return
    
    print(f"🔍 Analyzing commit {commit_hash[:8]}...")
    
    try:
        # Use the real semantic analyzer
        semantic_events = analyzer.analyze_commit(commit_hash)
        
        if semantic_events:
            stored_count, notes_success = svcs.analyze_and_store_commit(commit_hash, semantic_events)
            
            print(f"✅ Stored {stored_count} semantic events")
            if notes_success:
                print("📝 Semantic data saved as git notes")
            else:
                print("⚠️ Failed to save git notes")
        else:
            print("ℹ️ No semantic changes detected")
    
    except Exception as e:
        print(f"❌ Analysis error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="SVCS Repository-Local CLI - Git-Integrated Team Collaboration",
        epilog="Examples:\n"
               "  svcs-local init                    # Initialize SVCS for current repo\n"
               "  svcs-local status                  # Show repository status\n"
               "  svcs-local events --limit 10       # Show recent semantic events\n"
               "  svcs-local notes sync              # Sync semantic notes to remote\n"
               "  svcs-local migrate list            # List projects for migration\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--path", "-p", type=str, help="Repository path (default: current directory)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    parser_init = subparsers.add_parser("init", help="Initialize SVCS for repository")
    parser_init.set_defaults(func=cmd_init)
    
    # Status command
    parser_status = subparsers.add_parser("status", help="Show SVCS status")
    parser_status.set_defaults(func=cmd_status)
    
    # Events command
    parser_events = subparsers.add_parser("events", help="List semantic events")
    parser_events.add_argument("--branch", "-b", type=str, help="Branch to query (default: current)")
    parser_events.add_argument("--limit", "-l", type=int, default=20, help="Maximum events to show")
    parser_events.set_defaults(func=cmd_events)
    
    # Notes command
    parser_notes = subparsers.add_parser("notes", help="Manage git notes")
    parser_notes.add_argument("action", choices=["sync", "fetch", "show"], help="Notes action")
    parser_notes.add_argument("--remote", "-r", type=str, default="origin", help="Git remote")
    parser_notes.add_argument("--commit", "-c", type=str, help="Commit hash (for show action)")
    parser_notes.set_defaults(func=cmd_notes)
    
    # Migrate command
    parser_migrate = subparsers.add_parser("migrate", help="Migrate from global SVCS")
    parser_migrate.add_argument("action", choices=["list", "migrate"], help="Migration action")
    parser_migrate.add_argument("--global-db", type=str, help="Global database path")
    parser_migrate.add_argument("--project-path", type=str, help="Project path to migrate")
    parser_migrate.set_defaults(func=cmd_migrate)
    
    # Remove command
    parser_remove = subparsers.add_parser("remove", help="Remove SVCS from repository")
    parser_remove.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    parser_remove.set_defaults(func=cmd_remove)
    
    # Analyze command
    parser_analyze = subparsers.add_parser("analyze", help="Manually analyze a commit")
    parser_analyze.add_argument("--commit", "-c", type=str, help="Commit hash (default: HEAD)")
    parser_analyze.set_defaults(func=cmd_analyze)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
