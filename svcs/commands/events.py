#!/usr/bin/env python3
"""
SVCS Events Commands

Commands for listing and processing semantic events.
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path
from .base import RepositoryLocalSVCS, ensure_svcs_initialized, print_svcs_error


def cmd_events(args):
    """List semantic events for current branch."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
        
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        # Try different method names that might exist
        if hasattr(svcs, 'get_branch_events'):
            events = svcs.get_branch_events(branch=args.branch, limit=args.limit)
        elif hasattr(svcs, 'get_semantic_events'):
            events = svcs.get_semantic_events(branch=args.branch, limit=args.limit)
        else:
            print_svcs_error("Cannot find event retrieval method")
            return
        
        if not events:
            current_branch = svcs.get_current_branch()
            print(f"ℹ️ No semantic events found for branch: {current_branch}")
            return
        
        print(f"📊 Semantic Events ({len(events)} found)")
        print("=" * 60)
        
        for event in events:
            # Handle different timestamp formats
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"🔍 {event['event_type']}")
            print(f"   📝 {event['commit_hash'][:8]} | {event['branch']} | {event.get('author', 'N/A')} | {timestamp}")
            print(f"   🎯 {event['node_id']} @ {event['location']}")
            print(f"   💬 {event['details']}")
            print(f"   🧠 {event['reasoning']}")
            print()
            
    except Exception as e:
        print_svcs_error(f"Error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()


def cmd_process_hook(args):
    """Process git hook for semantic analysis."""
    hook_name = args.hook_name
    repo_path = Path(args.path or '.')
    
    # Determine the hook type and process accordingly
    if hook_name.endswith('post-commit'):
        # Post-commit: analyze the latest commit
        try:
            # Get the latest commit hash
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  cwd=repo_path, capture_output=True, text=True, check=True)
            commit_hash = result.stdout.strip()
            
            # Initialize SVCS and analyzer
            from svcs_repo_local import RepositoryLocalSVCS
            from svcs_repo_analyzer import RepositoryLocalSemanticAnalyzer
            
            print("🔍 SVCS: Analyzing semantic changes...")
            svcs = RepositoryLocalSVCS(str(repo_path))
            analyzer = RepositoryLocalSemanticAnalyzer(str(repo_path))
            
            # Analyze the commit
            semantic_events = analyzer.analyze_commit(commit_hash)
            if semantic_events:
                stored_count, notes_success = svcs.analyze_and_store_commit(commit_hash, semantic_events)
                print(f'✅ SVCS: Stored {stored_count} semantic events')
                if notes_success:
                    print('📝 SVCS: Semantic data saved as git notes')
                else:
                    print('⚠️ SVCS: Failed to save git notes')
            else:
                print('ℹ️ SVCS: No semantic changes detected')
                
        except subprocess.CalledProcessError as e:
            print(f"❌ SVCS: Git command failed: {e}")
        except Exception as e:
            print(f"❌ SVCS: Analysis error: {e}")
            
    elif hook_name.endswith('post-merge'):
        # Post-merge: handle merge analysis and transfer semantic events
        try:
            print("🔍 SVCS: Processing merge...")
            
            # Initialize SVCS
            from svcs_repo_local import RepositoryLocalSVCS
            svcs = RepositoryLocalSVCS(str(repo_path))
            
            # First, import semantic events from git notes (for commits merged from remote)
            imported_count = svcs.import_semantic_events_from_notes()
            if imported_count > 0:
                print(f"📥 SVCS: Imported {imported_count} semantic events from git notes")
            
            # Then, automatically process merge and transfer semantic events between branches
            result = svcs.process_merge()
            print(f"✅ SVCS: {result}")
            
        except Exception as e:
            print(f"❌ SVCS: Merge processing error: {e}")
        
    elif hook_name.endswith('post-checkout'):
        # Post-checkout: handle branch switching
        print("🔍 SVCS: Processing checkout...")
        # Additional checkout processing can be added here
        
    elif hook_name.endswith('pre-push'):
        # Pre-push: validation or sync
        print("🔍 SVCS: Processing pre-push...")
        # Additional pre-push processing can be added here
        
    else:
        print(f"⚠️ SVCS: Unknown hook type: {hook_name}")
