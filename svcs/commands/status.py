#!/usr/bin/env python3
"""
SVCS Status and Cleanup Commands

Commands for showing repository status and performing maintenance.
"""

from datetime import datetime
from pathlib import Path
from .base import RepositoryLocalSVCS, ensure_svcs_initialized, print_svcs_error


def cmd_status(args):
    """Show SVCS status for current repository."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    # Check if SVCS is initialized
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error(f"SVCS not initialized for repository: {repo_path}")
        print("Run 'svcs init' to initialize SVCS for this repository.")
        return
    
    svcs = RepositoryLocalSVCS(repo_path)
    status = svcs.get_repository_status()
    
    print(f"✅ SVCS Repository Status")
    print(f"📁 Repository: {status['repository_path']}")
    print(f"🌿 Current branch: {status['current_branch']}")
    print(f"🔢 Semantic events: {status['semantic_events_count']}")
    print(f"📝 Commits analyzed: {status['commits_analyzed']}")
    print(f"📅 Initialized: {datetime.fromtimestamp(status['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_cleanup(args):
    """Repository maintenance and cleanup."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🧹 Running cleanup for repository: {repo_path.name}")
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        if args.git_unreachable:
            print("🔍 Cleaning semantic events for unreachable commits...")
            result = svcs.cleanup_unreachable_commits()
            print(result)
            
        elif args.show_stats:
            print("📊 Repository database statistics:")
            stats = svcs.get_database_stats()
            if isinstance(stats, dict):
                print(f"📈 Total events: {stats.get('total_events', 'N/A')}")
                print(f"📝 Commits tracked: {stats.get('commits_tracked', 'N/A')}")
                print(f"💾 Database size: {stats.get('database_size', 'N/A')}")
                
        else:
            print("🧹 Running general cleanup...")
            result = svcs.cleanup_orphaned_data()
            print(result)
            
    except Exception as e:
        print_svcs_error(f"Error: {e}")
