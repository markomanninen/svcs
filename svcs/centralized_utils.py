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
        "database_path": ".svcs/semantic.db",
        "installation_type": "centralized"
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
        
        # Hook template that calls centralized SVCS
        hook_template = f"""#!/bin/bash
# SVCS Git Hook - Centralized Version
# This hook calls the centralized SVCS installation

{svcs_cmd} process-hook "$0" "$@"
"""
        
        # Install hooks
        hooks_to_install = ['post-commit', 'post-merge', 'post-checkout', 'pre-push']
        installed_hooks = []
        
        for hook_name in hooks_to_install:
            hook_path = hooks_dir / hook_name
            hook_path.write_text(hook_template)
            hook_path.chmod(0o755)  # Make executable
            installed_hooks.append(hook_name)
        
        print(f"✅ Installed centralized git hooks: {', '.join(installed_hooks)}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up git hooks: {e}")
        return False


def migrate_legacy_installation(repo_path: Path):
    """Migrate from legacy file-copy installation to centralized architecture."""
    svcs_dir = repo_path / '.svcs'
    
    if not svcs_dir.exists():
        return False
    
    # Check if this is a legacy installation (has copied Python files)
    legacy_files = ['svcs_repo_local.py', 'svcs_repo_analyzer.py', 'svcs_multilang.py']
    has_legacy_files = any((svcs_dir / f).exists() for f in legacy_files)
    
    if not has_legacy_files:
        return False
    
    print("🔄 Legacy SVCS installation detected.")
    response = input("Migrate to centralized version? This will remove local copies but preserve your data. (y/n): ").lower().strip()
    
    if response not in ['y', 'yes']:
        return False
    
    # Backup semantic database
    db_path = svcs_dir / 'semantic.db'
    if db_path.exists():
        backup_path = svcs_dir / 'semantic.db.backup'
        import shutil
        shutil.copy2(db_path, backup_path)
        print("📦 Backed up semantic database")
    
    # Remove legacy files
    for file in legacy_files + ['analyzer.py', 'api.py']:
        file_path = svcs_dir / file
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ Removed {file}")
    
    # Initialize centralized version
    result = init_svcs_centralized(repo_path)
    print("✅ Migration completed successfully")
    return True


def detect_svcs_state(repo_path: Path):
    """Detect current SVCS installation state."""
    svcs_dir = repo_path / '.svcs'
    
    if not svcs_dir.exists():
        return "not_initialized"
    
    config_path = svcs_dir / 'config.json'
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            if config.get("centralized"):
                return "centralized"
        except:
            pass
    
    # Check for legacy files
    legacy_files = ['svcs_repo_local.py', 'svcs_repo_analyzer.py']
    if any((svcs_dir / f).exists() for f in legacy_files):
        return "legacy"
    
    return "unknown"


# Maintain backward compatibility
def setup_repository_files(repo_path: Path):
    """Backward compatibility wrapper."""
    state = detect_svcs_state(repo_path)
    
    if state == "legacy":
        migrate_legacy_installation(repo_path)
        return True
    elif state == "centralized":
        print("✅ Already using centralized architecture")
        return True
    else:
        return init_svcs_centralized(repo_path).startswith("✅")
