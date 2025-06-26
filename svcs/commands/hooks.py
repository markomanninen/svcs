#!/usr/bin/env python3
"""
SVCS Hook Processing Commands

Commands for processing git hooks with semantic note synchronization.
"""

import subprocess
import sys
from pathlib import Path
from .base import print_svcs_info, print_svcs_success, print_svcs_error


def cmd_process_hook(args):
    """Process git hook with semantic analysis and note synchronization."""
    hook_name = args.hook_name
    hook_args = args.hook_args
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    print_svcs_info(f"Processing {hook_name} hook...")
    
    try:
        # Handle different types of hooks
        if hook_name == 'post-commit':
            return process_post_commit_hook(repo_path, hook_args)
        elif hook_name == 'post-merge':
            return process_post_merge_hook(repo_path, hook_args)
        elif hook_name == 'post-checkout':
            return process_post_checkout_hook(repo_path, hook_args)
        elif hook_name == 'pre-push':
            return process_pre_push_hook(repo_path, hook_args)
        else:
            print_svcs_info(f"No specific processing for {hook_name} hook")
            return True
            
    except Exception as e:
        print_svcs_error(f"Hook processing failed: {e}")
        return False


def process_post_commit_hook(repo_path: Path, hook_args):
    """Process post-commit hook - trigger semantic analysis."""
    try:
        # Get the latest commit hash
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              cwd=repo_path, capture_output=True, text=True, check=True)
        commit_hash = result.stdout.strip()
        
        print_svcs_info(f"Analyzing commit {commit_hash[:8]} for semantic events...")
        
        # Trigger semantic analysis for the commit
        from svcs_repo_local import RepositoryLocalSVCS
        svcs = RepositoryLocalSVCS(str(repo_path))
        
        # Process the latest commit
        result = svcs.analyze_current_commit()
        if result:
            print_svcs_success("Semantic analysis completed")
        else:
            print_svcs_info("No semantic events detected in this commit")
            
        return True
        
    except Exception as e:
        print_svcs_error(f"Post-commit analysis failed: {e}")
        return False


def process_post_merge_hook(repo_path: Path, hook_args):
    """Process post-merge hook - sync semantic notes."""
    try:
        print_svcs_info("Synchronizing semantic notes after merge...")
        
        # Fetch semantic notes from origin
        result = subprocess.run(['git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'], 
                              cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_svcs_success("Semantic notes synchronized from origin")
            
            # Import the fetched semantic notes into local database
            try:
                from svcs_repo_local import RepositoryLocalSVCS
                svcs = RepositoryLocalSVCS(str(repo_path))
                imported_count = svcs.import_semantic_events_from_notes()
                if imported_count > 0:
                    print_svcs_success(f"Imported {imported_count} semantic events from notes")
                else:
                    print_svcs_info("No new semantic events to import")
            except Exception as e:
                print_svcs_error(f"Failed to import semantic notes: {e}")
        else:
            print_svcs_info("No semantic notes found on origin")
            
        # Also trigger analysis of merge commit if it exists
        try:
            merge_result = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD^2'], 
                                        cwd=repo_path, capture_output=True, text=True)
            if merge_result.returncode == 0:
                # This is a merge commit, analyze it
                from svcs_repo_local import RepositoryLocalSVCS
                svcs = RepositoryLocalSVCS(str(repo_path))
                svcs.analyze_current_commit()
                print_svcs_success("Merge commit analyzed for semantic events")
        except:
            pass  # Not a merge commit or analysis failed
            
        return True
        
    except Exception as e:
        print_svcs_error(f"Post-merge processing failed: {e}")
        return False


def process_post_checkout_hook(repo_path: Path, hook_args):
    """Process post-checkout hook - fetch semantic notes after clone/checkout."""
    try:
        # Check if this is after a clone (no previous HEAD) or branch switch
        if len(hook_args) >= 3:
            prev_head = hook_args[0]
            new_head = hook_args[1]
            branch_checkout = hook_args[2] == '1'
            
            if prev_head == '0000000000000000000000000000000000000000':
                # This is after a clone
                print_svcs_info("Initial clone detected, fetching semantic notes...")
            elif branch_checkout:
                # This is a branch checkout
                print_svcs_info("Branch checkout detected, synchronizing semantic notes...")
            else:
                # File checkout, no need to sync notes
                return True
        
        # Fetch semantic notes from origin
        result = subprocess.run(['git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'], 
                              cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_svcs_success("Semantic notes fetched from origin")
            
            # Import the fetched semantic notes into local database
            try:
                from svcs_repo_local import RepositoryLocalSVCS
                svcs = RepositoryLocalSVCS(str(repo_path))
                imported_count = svcs.import_semantic_events_from_notes()
                if imported_count > 0:
                    print_svcs_success(f"Imported {imported_count} semantic events from notes")
                else:
                    print_svcs_info("No new semantic events to import")
            except Exception as e:
                print_svcs_error(f"Failed to import semantic notes: {e}")
        else:
            print_svcs_info("No semantic notes found on origin")
            
        return True
        
    except Exception as e:
        print_svcs_error(f"Post-checkout processing failed: {e}")
        return False


def process_pre_push_hook(repo_path: Path, hook_args):
    """Process pre-push hook - push semantic notes before code."""
    try:
        print_svcs_info("Checking for semantic notes to push...")
        
        # Check if we have semantic notes to push
        notes_check = subprocess.run(['git', 'notes', '--ref=refs/notes/svcs-semantic', 'list'], 
                                   cwd=repo_path, capture_output=True, text=True)
        
        if notes_check.returncode == 0 and notes_check.stdout.strip():
            print_svcs_info("Pushing semantic notes to origin...")
            
            # Push semantic notes
            push_result = subprocess.run(['git', 'push', 'origin', 'refs/notes/svcs-semantic'], 
                                       cwd=repo_path, capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print_svcs_success("Semantic notes pushed to origin")
            else:
                # Don't fail the push if notes push fails
                print_svcs_error(f"Failed to push semantic notes: {push_result.stderr}")
                print_svcs_info("Continuing with code push...")
        else:
            print_svcs_info("No semantic notes to push")
            
        return True
        
    except Exception as e:
        print_svcs_error(f"Pre-push processing failed: {e}")
        # Don't fail the push if hook processing fails
        return True
