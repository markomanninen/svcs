#!/usr/bin/env python3
"""
SVCS Git Notes Commands

Commands for managing git notes for team collaboration.
"""

import json
import subprocess
from pathlib import Path
from .base import ensure_svcs_initialized, print_svcs_error


def cmd_notes(args):
    """Git notes management for team collaboration."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        from svcs_repo_local import RepositoryLocalSVCS
        svcs = RepositoryLocalSVCS(str(repo_path))
        notes_manager = svcs.git_notes
        
        if args.notes_action == 'sync':
            print("🔄 Syncing semantic notes to remote...")
            result = notes_manager.sync_notes_to_remote()
            if result:
                print("✅ Semantic notes synced successfully")
            else:
                print("⚠️  Failed to sync semantic notes")
            
        elif args.notes_action == 'fetch':
            print("📥 Fetching semantic notes from remote...")
            result = notes_manager.fetch_notes_from_remote()
            if result:
                print("✅ Semantic notes fetched successfully")
            else:
                print("ℹ️  No new semantic notes to fetch")
            
        elif args.notes_action == 'show':
            commit_hash = args.commit or 'HEAD'
            print(f"📝 Showing semantic note for commit: {commit_hash}")
            note = notes_manager.get_semantic_data_from_note(commit_hash)
            if note:
                print(json.dumps(note, indent=2))
            else:
                print("ℹ️ No semantic note found for this commit")
                
        elif args.notes_action == 'status':
            print("📊 Git notes status:")
            # Check local notes
            local_notes_result = subprocess.run([
                "git", "notes", "--ref", "refs/notes/svcs-semantic", "list"
            ], cwd=repo_path, capture_output=True, text=True)
            
            local_count = len(local_notes_result.stdout.strip().split('\n')) if local_notes_result.stdout.strip() else 0
            print(f"Local notes: {local_count}")
            
            # Check remote notes
            remote_check = subprocess.run([
                "git", "ls-remote", "origin", "refs/notes/svcs-semantic"
            ], cwd=repo_path, capture_output=True, text=True)
            
            if remote_check.returncode == 0 and remote_check.stdout.strip():
                print("Remote status: ✅ Available")
            else:
                print("Remote status: ⚠️  Not available")
            
    except ImportError:
        print_svcs_error("Git notes functionality not available")
    except Exception as e:
        print_svcs_error(f"Error: {e}")
