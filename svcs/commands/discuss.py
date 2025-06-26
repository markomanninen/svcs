#!/usr/bin/env python3
"""
SVCS Conversational Interface Commands

Commands for natural language interaction with semantic data.
"""

import os
import sys
from pathlib import Path
from .base import ensure_svcs_initialized, print_svcs_error


def cmd_discuss(args):
    """Start conversational interface."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🤖 Starting conversational interface for repository: {repo_path.name}")
    print("💬 Ask questions about your code's semantic evolution...")
    print("💡 Examples: 'show performance optimizations', 'what changed in main branch'")
    
    # Handle initial query if provided
    if hasattr(args, 'query') and args.query:
        print(f"📝 Processing initial query: '{args.query}'")
        print()
        
        # First process the initial query
        try:
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            sys.path.insert(0, str(repo_path.parent))
            import svcs_repo_discuss
            
            # Process the initial query
            result = svcs_repo_discuss.process_query(args.query)
            print("🔍 Response:")
            print(result)
            print("\n" + "─" * 60 + "\n")
            
        except Exception as e:
            print_svcs_error(f"Error processing initial query: {e}")
        
        # Ask if user wants to continue with interactive session
        print("💬 Continue with interactive conversation? (y/n): ", end="")
        response = input().strip().lower()
        if response not in ['y', 'yes', '']:
            os.chdir(original_dir)
            return
    
    print("⏹️ Type 'exit' or 'quit' to end the session")
    print()
    
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        sys.path.insert(0, str(repo_path.parent))
        import svcs_repo_discuss
        
        # Start interactive session
        svcs_repo_discuss.start_interactive_session()
        
        os.chdir(original_dir)
        
    except Exception as e:
        print_svcs_error(f"Error: {e}")
        os.chdir(original_dir)


def cmd_query(args):
    """One-shot natural language query."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    print(f"🤖 Processing query: '{args.query}'")
    
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        sys.path.insert(0, str(repo_path.parent))
        import svcs_repo_discuss
        
        # Process single query
        result = svcs_repo_discuss.process_query(args.query)
        print(result)
        
        os.chdir(original_dir)
        
    except Exception as e:
        print_svcs_error(f"Error: {e}")
        os.chdir(original_dir)
