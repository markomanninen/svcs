#!/usr/bin/env python3
"""
SVCS Sync and Merge Commands

Commands for syncing semantic data and handling merge operations.
"""

import subprocess
from pathlib import Path
from .base import RepositoryLocalSVCS, ensure_svcs_initialized, print_svcs_error


def cmd_sync(args):
    """Sync semantic data with remote repository."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔄 Syncing semantic data with remote...")
        
        # 1. Push local semantic notes to remote
        push_success = svcs.git_notes.sync_notes_to_remote()
        if push_success:
            print("📤 Pushed local semantic notes to remote")
        
        # 2. Fetch semantic notes from remote
        fetch_success = svcs.git_notes.fetch_notes_from_remote()
        if fetch_success:
            print("📥 Fetched semantic notes from remote")
            
            # 3. Import semantic events from fetched notes
            imported = svcs.import_semantic_events_from_notes()
            if imported > 0:
                print(f"📊 Imported {imported} semantic events from remote notes")
        
        # 4. Process any pending merges
        merge_result = svcs.process_merge()
        if "No source branch detected" not in merge_result:
            print(f"🔀 {merge_result}")
        
        print("✅ Semantic data sync completed")
        
    except Exception as e:
        print_svcs_error(f"Sync error: {e}")


def cmd_merge_resolve(args):
    """Automatically resolve post-merge semantic event issues."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔍 Checking for post-merge semantic event issues...")
        
        # Import semantic events from git notes first
        imported = svcs.import_semantic_events_from_notes()
        if imported > 0:
            print(f"📥 Imported {imported} semantic events from git notes")
        
        # Process merge event transfer
        merge_result = svcs.process_merge()
        print(f"🔀 {merge_result}")
        
        # Show final status
        status = svcs.get_repository_status()
        print(f"📊 Final status: {status['semantic_events_count']} semantic events on {status['current_branch']}")
        
    except Exception as e:
        print_svcs_error(f"Merge resolve error: {e}")


def cmd_auto_fix(args):
    """Automatically detect and fix common SVCS issues after git operations."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔧 Auto-detecting and fixing SVCS issues...")
        
        result = svcs.auto_resolve_merge()
        print(f"🔀 {result}")
        
        print("✅ Auto-fix completed")
        
    except Exception as e:
        print_svcs_error(f"Auto-fix error: {e}")


def cmd_sync_all(args):
    """Complete sync after git operations - fetches, imports, and resolves everything."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔄 Complete SVCS sync - fetching, importing, and resolving...")
        print()
        
        # Step 1: Try to sync with remote
        print("📡 Step 1: Syncing with remote...")
        try:
            # Push/pull semantic notes
            svcs.git_notes.sync_notes_to_remote()
            svcs.git_notes.fetch_notes_from_remote()
            print("✅ Remote sync completed")
        except Exception as e:
            print(f"ℹ️ Remote sync skipped: {str(e)[:50]}...")
        
        # Step 2: Import any semantic events from notes
        print("📥 Step 2: Importing semantic events from git notes...")
        imported = svcs.import_semantic_events_from_notes()
        if imported > 0:
            print(f"✅ Imported {imported} semantic events")
        else:
            print("ℹ️ No new semantic events to import")
        
        # Step 3: Process any pending merges
        print("🔀 Step 3: Processing merge operations...")
        merge_result = svcs.process_merge()
        if "No source branch detected" not in merge_result and "No new semantic events" not in merge_result:
            print(f"✅ {merge_result}")
        else:
            print("ℹ️ No pending merge operations")
        
        # Step 4: Final status
        print("📊 Step 4: Final status check...")
        status = svcs.get_repository_status()
        print(f"✅ Repository: {status['semantic_events_count']} semantic events on {status['current_branch']}")
        
        print()
        print("🎉 Complete sync finished! Your semantic data is now up-to-date.")
        
    except Exception as e:
        print_svcs_error(f"Sync error: {e}")


def cmd_pull(args):
    """Enhanced git pull that automatically handles semantic notes sync."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔄 Enhanced git pull with semantic data sync...")
        
        # Step 1: Regular git pull
        print("📥 Step 1: Pulling latest changes from remote...")
        result = subprocess.run(['git', 'pull'], cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git pull completed successfully")
            if result.stdout.strip():
                print(f"ℹ️  {result.stdout.strip()}")
        else:
            print(f"⚠️  Git pull had issues: {result.stderr}")
            # Continue with semantic sync even if pull had issues
        
        # Step 2: Fetch semantic notes from remote
        print("📥 Step 2: Fetching semantic notes from remote...")
        fetch_result = svcs.git_notes.fetch_notes_from_remote()
        if fetch_result:
            print("✅ Semantic notes fetched successfully")
        else:
            print("ℹ️  No new semantic notes to fetch")
        
        # Step 3: Import semantic events from notes
        print("📊 Step 3: Importing semantic events from notes...")
        imported_count = svcs.import_semantic_events_from_notes()
        if imported_count > 0:
            print(f"✅ Imported {imported_count} semantic events")
        else:
            print("ℹ️  No new semantic events to import")
        
        # Step 4: Process any merge operations
        print("🔀 Step 4: Processing merge operations...")
        merge_result = svcs.process_merge()
        if "No source branch detected" not in merge_result:
            print(f"✅ {merge_result}")
        else:
            print("ℹ️  No merge operations needed")
        
        print("🎉 Enhanced pull completed! Code and semantic data are now synchronized.")
        
    except Exception as e:
        print_svcs_error(f"Enhanced pull error: {e}")


def cmd_merge(args):
    """Enhanced git merge with automatic semantic event transfer."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🔀 SVCS: Enhanced merge of branch '{args.branch}'...")
    
    merge_args = ['git', 'merge']
    if args.no_ff:
        merge_args.append('--no-ff')
    if args.message:
        merge_args.extend(['-m', args.message])
    merge_args.append(args.branch)
    
    try:
        # Perform git merge
        merge_result = subprocess.run(merge_args, cwd=repo_path, capture_output=True, text=True, check=True)
        
        print("✅ Git merge completed:")
        print(merge_result.stdout)
        
        # Automatically transfer semantic events (handled by post-merge hook)
        if args.manual_transfer:
            print("🔄 Manually processing semantic event transfer...")
            svcs = RepositoryLocalSVCS(repo_path)
            result = svcs.process_merge(source_branch=args.branch)
            print(f"📊 {result}")
            
    except subprocess.CalledProcessError as e:
        print_svcs_error(f"Git merge failed: {e.stderr}")
        print("ℹ️ You may need to resolve conflicts manually")
    except Exception as e:
        print_svcs_error(f"Error during enhanced merge: {e}")


def cmd_push(args):
    """Enhanced git push that automatically syncs semantic notes."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        print("🔄 Enhanced git push with semantic notes sync...")
        
        # Step 1: Sync semantic notes to remote first
        print("📤 Step 1: Syncing semantic notes to remote...")
        sync_result = svcs.git_notes.sync_notes_to_remote()
        if sync_result:
            print("✅ Semantic notes synced to remote")
        else:
            print("⚠️  Failed to sync semantic notes (continuing with push)")
        
        # Step 2: Regular git push
        print("📤 Step 2: Pushing code changes to remote...")
        push_args = []
        if hasattr(args, 'remote') and args.remote:
            push_args.append(args.remote)
        if hasattr(args, 'branch') and args.branch:
            push_args.append(args.branch)
            
        result = subprocess.run(['git', 'push'] + push_args, cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git push completed successfully")
            if result.stdout.strip():
                print(f"ℹ️  {result.stdout.strip()}")
        else:
            print(f"❌ Git push failed: {result.stderr}")
            return
        
        print("🎉 Enhanced push completed! Code and semantic notes are now on remote.")
        
    except Exception as e:
        print_svcs_error(f"Enhanced push error: {e}")


def cmd_config(args):
    """Configure SVCS settings for automatic sync behavior."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        svcs = RepositoryLocalSVCS(repo_path)
        
        if args.config_action == 'set':
            if args.setting == 'auto-sync' and args.value:
                auto_sync = args.value.lower() in ['true', '1', 'yes', 'on']
                svcs.set_config('auto_sync_notes', auto_sync)
                status = "enabled" if auto_sync else "disabled"
                print(f"✅ Automatic semantic notes sync {status}")
                
                if auto_sync:
                    print("ℹ️  Git hooks will now automatically sync semantic notes during push/pull/merge operations")
                else:
                    print("ℹ️  Manual 'svcs notes sync/fetch' commands will be required")
                    
        elif args.config_action == 'get':
            if args.setting == 'auto-sync':
                auto_sync = svcs.get_config('auto_sync_notes', True)  # Default to True
                status = "enabled" if auto_sync else "disabled"
                print(f"Auto-sync semantic notes: {status}")
            else:
                print("Available settings:")
                print("  auto-sync  - Automatically sync semantic notes during git operations")
                
        elif args.config_action == 'list':
            config = svcs.get_all_config()
            print("Current SVCS configuration:")
            for key, value in config.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print_svcs_error(f"Configuration error: {e}")
