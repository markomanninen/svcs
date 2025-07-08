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
            from svcs.semantic_analyzer import SVCSModularAnalyzer
            
            print("🔍 SVCS: Analyzing semantic changes...")
            svcs = RepositoryLocalSVCS(str(repo_path))
            analyzer = SVCSModularAnalyzer(str(repo_path))
            
            # Analyze the commit using modern analyzer
            semantic_events = analyzer.analyze_commit_changes(commit_hash)
            if semantic_events:
                stored_count, notes_success = svcs.analyze_and_store_commit(commit_hash, semantic_events)
                print(f'✅ SVCS: Stored {stored_count} semantic events')
            else:
                print('ℹ️ SVCS: No semantic changes detected')
                
        except subprocess.CalledProcessError as e:
            print(f"❌ SVCS: Git command failed: {e}")
        except Exception as e:
            print(f"❌ SVCS: Analysis error: {e}")
            
    elif hook_name.endswith('post-merge'):
        # Post-merge: handle merge analysis and transfer semantic events
        try:
            # Initialize SVCS
            from svcs_repo_local import RepositoryLocalSVCS
            svcs = RepositoryLocalSVCS(str(repo_path))
            
            # Check if auto-sync is enabled (default: True)
            auto_sync = svcs.get_config('auto_sync_notes', True)
            
            if auto_sync:
                # Automatically fetch semantic notes from remote (in case they weren't fetched during git pull)
                fetch_result = svcs.git_notes.fetch_notes_from_remote()
                if fetch_result:
                    pass  # Successfully fetched, no need to announce
            else:
                print("ℹ️ SVCS: Auto-sync disabled, use 'svcs notes fetch' manually if needed")
            
            # Import semantic events from git notes (for commits merged from remote)
            imported_count = svcs.import_semantic_events_from_notes()
            if imported_count > 0:
                print(f"✅ SVCS: Imported {imported_count} semantic events")
            
            # Finally, automatically process merge and transfer semantic events between branches
            result = svcs.process_merge()
            print(f"{result}")  # This already includes ✅ SVCS: prefix
            
        except Exception as e:
            print(f"❌ SVCS: Merge processing error: {e}")
        
    elif hook_name.endswith('post-checkout'):
        # Post-checkout: handle branch switching and fetch notes
        try:
            # Initialize SVCS
            from svcs_repo_local import RepositoryLocalSVCS
            svcs = RepositoryLocalSVCS(str(repo_path))
            
            # Fetch semantic notes when switching branches (they might have new commits)
            fetch_result = svcs.git_notes.fetch_notes_from_remote()
            
            # Import any new semantic events from notes
            imported_count = svcs.import_semantic_events_from_notes()
            if imported_count > 0:
                print(f"✅ SVCS: Imported {imported_count} semantic events")
            elif fetch_result:
                print("✅ SVCS: Semantic notes synced")
                
        except Exception as e:
            print(f"❌ SVCS: Checkout processing error: {e}")
        
    elif hook_name.endswith('pre-push'):
        # Pre-push: automatically sync semantic notes to remote (if auto-sync enabled)
        try:
            print("🔍 SVCS: Processing pre-push...")
            
            # Initialize SVCS
            from svcs_repo_local import RepositoryLocalSVCS
            svcs = RepositoryLocalSVCS(str(repo_path))
            
            # Check if auto-sync is enabled (default: True)
            auto_sync = svcs.get_config('auto_sync_notes', True)
            
            if auto_sync:
                # Automatically sync semantic notes to remote before push
                print("📤 SVCS: Auto-syncing semantic notes to remote...")
                sync_result = svcs.git_notes.sync_notes_to_remote()
                if sync_result:
                    print("✅ SVCS: Semantic notes synced to remote")
                else:
                    print("⚠️ SVCS: Failed to sync semantic notes (continuing with push)")
            else:
                print("ℹ️ SVCS: Auto-sync disabled, use 'svcs notes sync' manually if needed")
                
        except Exception as e:
            print(f"❌ SVCS: Pre-push processing error: {e}")
            # Don't fail the push if semantic notes sync fails
        
    elif hook_name.endswith('post-receive'):
        # Post-receive: analyze pushed commits in bare repository
        try:
            import sys
            from svcs_repo_local import RepositoryLocalSVCS
            from svcs.semantic_analyzer import SVCSModularAnalyzer
            
            print("📥 SVCS: Processing pushed commits...")
            svcs = RepositoryLocalSVCS(str(repo_path))
            analyzer = SVCSModularAnalyzer(str(repo_path))
            
            total_analyzed = 0
            
            # Read stdin for pushed refs (format: old-sha new-sha ref-name)
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 3:
                    old_sha, new_sha, ref_name = parts[0], parts[1], parts[2]
                    
                    # Only process branch updates (not tags or notes)
                    if ref_name.startswith('refs/heads/'):
                        branch_name = ref_name.replace('refs/heads/', '')
                        
                        # Get list of new commits
                        if old_sha == '0000000000000000000000000000000000000000':
                            # New branch - analyze recent commits (limit to avoid overwhelming)
                            commit_range = f"{new_sha} --max-count=10"
                        else:
                            # Updated branch - analyze new commits
                            commit_range = f"{old_sha}..{new_sha}"
                        
                        # Get commit hashes
                        result = subprocess.run(['git', 'rev-list', '--reverse'] + commit_range.split(), 
                                              cwd=repo_path, capture_output=True, text=True, check=True)
                        commit_hashes = [c.strip() for c in result.stdout.split('\n') if c.strip()]
                        
                        # Analyze each new commit
                        branch_analyzed = 0
                        for commit_hash in commit_hashes:
                            try:
                                semantic_events = analyzer.analyze_commit_changes(commit_hash)
                                if semantic_events:
                                    stored_count, _ = svcs.analyze_and_store_commit(commit_hash, semantic_events)
                                    branch_analyzed += stored_count
                            except Exception as e:
                                print(f"⚠️ SVCS: Failed to analyze commit {commit_hash[:8]}: {e}")
                        
                        if branch_analyzed > 0:
                            print(f"✅ SVCS: Analyzed {branch_analyzed} semantic events for {branch_name}")
                        total_analyzed += branch_analyzed
            
            if total_analyzed == 0:
                print("ℹ️ SVCS: No semantic changes detected in pushed commits")
            else:
                print(f"✅ SVCS: Total {total_analyzed} semantic events analyzed")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ SVCS: Git command failed: {e}")
        except Exception as e:
            print(f"❌ SVCS: Post-receive processing error: {e}")
    
    elif hook_name.endswith('update'):
        # Update: handle reference updates (especially semantic notes)
        try:
            # Get arguments: ref-name old-sha new-sha
            if len(args.hook_args) >= 3:
                ref_name = args.hook_args[0]
                old_sha = args.hook_args[1]
                new_sha = args.hook_args[2]
                
                # Handle semantic notes updates
                if ref_name == 'refs/notes/svcs-semantic':
                    print("📝 SVCS: Processing semantic notes update...")
                    
                    from svcs_repo_local import RepositoryLocalSVCS
                    svcs = RepositoryLocalSVCS(str(repo_path))
                    
                    # Import updated semantic events from notes
                    imported_count = svcs.import_semantic_events_from_notes()
                    if imported_count > 0:
                        print(f"✅ SVCS: Imported {imported_count} semantic events from notes")
                    else:
                        print("ℹ️ SVCS: No new semantic events to import")
                else:
                    # For other refs, just acknowledge
                    print(f"🔄 SVCS: Reference {ref_name} updated ({old_sha[:8]}..{new_sha[:8]})")
            else:
                print("⚠️ SVCS: Update hook called with insufficient arguments")
                
        except Exception as e:
            print(f"❌ SVCS: Update processing error: {e}")
        
    else:
        print(f"⚠️ SVCS: Unknown hook type: {hook_name}")
