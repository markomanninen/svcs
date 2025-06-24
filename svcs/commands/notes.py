#!/usr/bin/env python3
"""
SVCS Git Notes Commands

Commands for managing git notes for team collaboration.
"""

from pathlib import Path
from .base import ensure_svcs_initialized, print_svcs_error


def cmd_notes(args):
    """Git notes management for team collaboration."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        from svcs_repo_local import SVCSGitNotes
        notes_manager = SVCSGitNotes(str(repo_path))
        
        if args.notes_action == 'sync':
            print("🔄 Syncing semantic notes to remote...")
            result = notes_manager.sync_to_remote()
            print(result)
            
        elif args.notes_action == 'fetch':
            print("📥 Fetching semantic notes from remote...")
            result = notes_manager.fetch_from_remote()
            print(result)
            
        elif args.notes_action == 'show':
            commit_hash = args.commit or 'HEAD'
            print(f"📝 Showing semantic note for commit: {commit_hash}")
            note = notes_manager.get_note(commit_hash)
            if note:
                print(note)
            else:
                print("ℹ️ No semantic note found for this commit")
                
        elif args.notes_action == 'status':
            print("📊 Git notes status:")
            status = notes_manager.get_sync_status()
            print(f"Local notes: {status.get('local_count', 0)}")
            print(f"Remote status: {status.get('remote_status', 'Unknown')}")
            
    except ImportError:
        print_svcs_error("Git notes functionality not available")
    except Exception as e:
        print_svcs_error(f"Error: {e}")
