#!/usr/bin/env python3
"""
SVCS Global Git Hook Manager

This module manages git hooks across multiple projects by:
1. Installing a global hook script in ~/.svcs/hooks/
2. Creating symlinks from project .git/hooks/ to the global script
3. Routing analysis requests to the global MCP server
"""

import os
import stat
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class GitHookManager:
    """Manages global git hooks for SVCS projects."""
    
    def __init__(self, svcs_home: Path = None):
        self.svcs_home = svcs_home or Path.home() / ".svcs"
        self.hooks_dir = self.svcs_home / "hooks"
        self.global_hook_script = self.hooks_dir / "svcs-hook"
        self.ensure_hooks_directory()
    
    def ensure_hooks_directory(self):
        """Ensure the hooks directory exists."""
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
    
    def create_global_hook_script(self):
        """Create the global SVCS hook script."""
        hook_content = '''#!/bin/bash
#
# SVCS Global Git Hook
# Routes git hook events to the global SVCS MCP server
#

# Get the absolute path of the project
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$PROJECT_ROOT" ]; then
    echo "❌ SVCS: Not in a git repository"
    exit 1
fi

# Get the hook type from the script name
HOOK_TYPE=$(basename "$0")

# Check if this project is registered with SVCS
if ! svcs status --path "$PROJECT_ROOT" --quiet >/dev/null 2>&1; then
    # Project not registered, skip SVCS analysis
    exit 0
fi

# Route to SVCS MCP server for analysis
case "$HOOK_TYPE" in
    "post-commit")
        echo "🔍 SVCS: Analyzing semantic changes..."
        svcs analyze-commit "$PROJECT_ROOT" "$@"
        ;;
    "pre-commit")
        echo "🔍 SVCS: Pre-commit analysis..."
        svcs analyze-pre-commit "$PROJECT_ROOT" "$@"
        ;;
    *)
        # For other hooks, just log the event
        svcs log-hook-event "$PROJECT_ROOT" "$HOOK_TYPE" "$@"
        ;;
esac

exit 0
'''
        
        # Write the script
        with open(self.global_hook_script, 'w') as f:
            f.write(hook_content)
        
        # Make it executable
        self.global_hook_script.chmod(0o755)
        logger.info(f"Created global hook script: {self.global_hook_script}")
    
    def install_project_hooks(self, project_path: str, hooks: List[str] = None) -> bool:
        """Install SVCS hooks for a specific project."""
        if hooks is None:
            hooks = ['post-commit', 'pre-commit']
        
        project_path = Path(project_path).resolve()
        git_hooks_dir = project_path / ".git" / "hooks"
        
        if not git_hooks_dir.exists():
            logger.error(f"Git hooks directory not found: {git_hooks_dir}")
            return False
        
        # Ensure global hook script exists
        if not self.global_hook_script.exists():
            self.create_global_hook_script()
        
        success_count = 0
        for hook_name in hooks:
            hook_path = git_hooks_dir / hook_name
            
            try:
                # Remove existing hook if it exists
                if hook_path.exists():
                    if hook_path.is_symlink():
                        hook_path.unlink()
                    else:
                        # Backup existing hook
                        backup_path = git_hooks_dir / f"{hook_name}.svcs-backup"
                        hook_path.rename(backup_path)
                        logger.info(f"Backed up existing hook: {backup_path}")
                
                # Create symlink to global hook
                hook_path.symlink_to(self.global_hook_script)
                logger.info(f"Installed {hook_name} hook for {project_path}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to install {hook_name} hook: {e}")
        
        return success_count == len(hooks)
    
    def uninstall_project_hooks(self, project_path: str, hooks: List[str] = None) -> bool:
        """Remove SVCS hooks from a specific project."""
        if hooks is None:
            hooks = ['post-commit', 'pre-commit']
        
        project_path = Path(project_path).resolve()
        git_hooks_dir = project_path / ".git" / "hooks"
        
        if not git_hooks_dir.exists():
            return True  # No hooks directory, nothing to remove
        
        success_count = 0
        for hook_name in hooks:
            hook_path = git_hooks_dir / hook_name
            backup_path = git_hooks_dir / f"{hook_name}.svcs-backup"
            
            try:
                if hook_path.exists() and hook_path.is_symlink():
                    # Check if it's our symlink
                    if hook_path.resolve() == self.global_hook_script.resolve():
                        hook_path.unlink()
                        logger.info(f"Removed {hook_name} hook from {project_path}")
                        
                        # Restore backup if it exists
                        if backup_path.exists():
                            backup_path.rename(hook_path)
                            logger.info(f"Restored backup hook: {hook_name}")
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to remove {hook_name} hook: {e}")
        
        return success_count == len(hooks)
    
    def get_project_hook_status(self, project_path: str) -> Dict[str, str]:
        """Get the status of SVCS hooks for a project."""
        project_path = Path(project_path).resolve()
        git_hooks_dir = project_path / ".git" / "hooks"
        
        status = {}
        for hook_name in ['post-commit', 'pre-commit']:
            hook_path = git_hooks_dir / hook_name
            
            if not hook_path.exists():
                status[hook_name] = "not_installed"
            elif hook_path.is_symlink():
                if hook_path.resolve() == self.global_hook_script.resolve():
                    status[hook_name] = "svcs_installed"
                else:
                    status[hook_name] = "other_symlink"
            else:
                status[hook_name] = "custom_script"
        
        return status
    
    def install_global_hooks(self) -> bool:
        """Install the global hook system."""
        try:
            self.create_global_hook_script()
            logger.info("Global SVCS hook system installed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to install global hooks: {e}")
            return False
    
    def list_hooked_projects(self) -> List[str]:
        """List all projects that have SVCS hooks installed."""
        # This would require scanning or maintaining a registry
        # For now, return empty list as this requires integration with ProjectManager
        return []


def install_hooks_for_project(project_path: str) -> bool:
    """Convenience function to install hooks for a project."""
    hook_manager = GitHookManager()
    return hook_manager.install_project_hooks(project_path)


def uninstall_hooks_for_project(project_path: str) -> bool:
    """Convenience function to uninstall hooks for a project."""
    hook_manager = GitHookManager()
    return hook_manager.uninstall_project_hooks(project_path)


if __name__ == "__main__":
    # CLI interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python git_hooks.py <install|uninstall|status> [project_path]")
        sys.exit(1)
    
    action = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    hook_manager = GitHookManager()
    
    if action == "install":
        success = hook_manager.install_project_hooks(project_path)
        print(f"Hook installation: {'✅ Success' if success else '❌ Failed'}")
    
    elif action == "uninstall":
        success = hook_manager.uninstall_project_hooks(project_path)
        print(f"Hook removal: {'✅ Success' if success else '❌ Failed'}")
    
    elif action == "status":
        status = hook_manager.get_project_hook_status(project_path)
        print(f"Hook status for {project_path}:")
        for hook, state in status.items():
            print(f"  {hook}: {state}")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
