#!/usr/bin/env python3
"""
SVCS Centralized Utils Module
Improved architecture with centralized installation
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to sys.path to find svcs_repo_registry_integration
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))


def smart_init_svcs(repo_path: Path):
    """Smart SVCS initialization with auto-detection."""
    git_exists = (repo_path / '.git').exists()
    svcs_exists = (repo_path / '.svcs').exists()
    has_files = any(repo_path.iterdir()) if repo_path.exists() else False
    
    # Check if SVCS already initialized
    if svcs_exists:
        return "✅ SVCS already initialized. Use 'svcs status' to check repository status."
    
    # If git exists, proceed with SVCS initialization
    if git_exists:
        return init_svcs_centralized(repo_path)
    
    # If directory is empty, auto-initialize both git and SVCS
    if not has_files:
        print(f"📁 Empty directory detected. Initializing git repository and SVCS...")
        try:
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            print("✅ Git repository initialized")
            return init_svcs_centralized(repo_path)
        except subprocess.CalledProcessError as e:
            return f"❌ Error: Failed to initialize git repository: {e}"
    
    # Directory has files but no git - prompt user
    print("📁 Directory contains files but no git repository.")
    response = input("Initialize git repository? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        try:
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            print("✅ Git repository initialized")
            return init_svcs_centralized(repo_path)
        except subprocess.CalledProcessError as e:
            return f"❌ Error: Failed to initialize git repository: {e}"
    else:
        return "❌ SVCS requires a git repository. Please run 'git init' first, then 'svcs init'."


def init_svcs_centralized(repo_path: Path):
    """Initialize SVCS with centralized architecture (no file copying)."""
    svcs_dir = repo_path / '.svcs'
    svcs_dir.mkdir(exist_ok=True)
    
    print(f"🔧 Initializing SVCS for repository: {repo_path}")
    
    # Create minimal local configuration instead of copying files
    config = {
        "svcs_version": "1.0.0",
        "initialized": True,
        "centralized": True,
        "database_path": ".svcs/semantic.db"
    }
    
    config_path = svcs_dir / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("📄 Created centralized SVCS configuration")
    
    # Set up centralized git hooks (reference global installation)
    if not setup_centralized_git_hooks(repo_path):
        return "❌ Failed to set up git hooks"
    
    # Initialize database and basic setup without hooks
    try:
        from svcs_repo_local import RepositoryLocalSVCS
        svcs = RepositoryLocalSVCS(str(repo_path))
        init_result = svcs.initialize_repository()
        
        # Register the repository in the central registry
        try:
            from svcs_repo_registry_integration import auto_register_after_init
            registration_result = auto_register_after_init(str(repo_path))
            print(f"📝 {registration_result}")
        except Exception as reg_error:
            print(f"⚠️ Warning: Failed to register repository in central registry: {reg_error}")
        
        # Get current branch for display
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=repo_path, capture_output=True, text=True, check=True)
            branch = result.stdout.strip() or 'main'
        except:
            branch = 'main'
        
        # Automatically fetch semantic notes if this is a cloned repository
        try:
            # Check if we have remotes configured (indicating this is a clone)
            remote_result = subprocess.run(['git', 'remote'], 
                                         cwd=repo_path, capture_output=True, text=True, check=True)
            if remote_result.stdout.strip():
                print("🔄 Checking for existing semantic notes...")
                fetch_result = subprocess.run(['git', 'fetch', 'origin', 'refs/notes/svcs-semantic:refs/notes/svcs-semantic'], 
                                            cwd=repo_path, capture_output=True, text=True)
                if fetch_result.returncode == 0:
                    print("✅ Existing semantic notes fetched from origin")
                    
                    # Import the fetched semantic notes into local database
                    try:
                        imported_count = svcs.import_semantic_events_from_notes()
                        if imported_count > 0:
                            print(f"✅ Imported {imported_count} semantic events from notes")
                        else:
                            print("ℹ️  No semantic events to import")
                    except Exception as e:
                        print(f"⚠️  Failed to import semantic notes: {e}")
                else:
                    print("ℹ️  No existing semantic notes found on origin")
        except:
            pass  # Not a big deal if this fails
            
        return f"✅ SVCS initialized for repository at {repo_path} (branch: {branch})"
    except Exception as e:
        return f"❌ Error during SVCS initialization: {e}"


def setup_centralized_git_hooks(repo_path: Path):
    """Set up git hooks that reference centralized SVCS installation."""
    hooks_dir = repo_path / '.git' / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    # Get path to centralized SVCS installation
    try:
        # Find the directory where this module is located (svcs/)
        current_dir = Path(__file__).parent
        cli_script = current_dir / 'cli.py'
        
        if not cli_script.exists():
            # Fallback to direct module execution
            svcs_cmd = f"{sys.executable} -m svcs.cli"
        else:
            # Use the proper modular CLI script
            svcs_cmd = f"{sys.executable} {cli_script}"
        
        # Enhanced hook templates with semantic note synchronization
        hooks_config = {
            'post-commit': f"""#!/bin/bash
# SVCS Post-Commit Hook - Trigger semantic analysis
echo "🔍 SVCS: Analyzing commit for semantic events..."
if [ -d ".svcs" ]; then
    {svcs_cmd} process-hook post-commit "$@" || echo "⚠️  SVCS: Post-commit analysis failed"
fi
""",
            'post-merge': f"""#!/bin/bash
# SVCS Post-Merge Hook - Sync semantic notes and analyze merge
if [ -d ".svcs" ]; then
    {svcs_cmd} process-hook post-merge "$@" || echo "⚠️  SVCS: Post-merge processing failed"
fi
""",
            'post-checkout': f"""#!/bin/bash
# SVCS Post-Checkout Hook - Fetch semantic notes after clone/checkout
if [ -d ".svcs" ]; then
    {svcs_cmd} process-hook post-checkout "$@" || echo "⚠️  SVCS: Post-checkout processing failed"
fi
""",
            'post-receive': f"""#!/bin/bash
# SVCS Post-Receive Hook - For bare repositories
echo "� SVCS: Post-receive hook executed"
""",
            'update': f"""#!/bin/bash
# SVCS Update Hook - For handling note updates in bare repos
echo "🔄 SVCS: Update hook executed"
"""
        }
        
        # Install enhanced hooks
        installed_hooks = []
        
        for hook_name, hook_content in hooks_config.items():
            hook_path = hooks_dir / hook_name
            hook_path.write_text(hook_content)
            hook_path.chmod(0o755)  # Make executable
            installed_hooks.append(hook_name)
        
        print(f"✅ Installed centralized git hooks: {', '.join(installed_hooks)}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up git hooks: {e}")
        return False


# Note: Only centralized architecture is supported. All transitional logic has been removed.
