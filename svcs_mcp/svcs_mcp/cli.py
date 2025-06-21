#!/usr/bin/env python3
"""
SVCS CLI - Command-line interface for SVCS MCP.

Provides easy commands for managing SVCS projects:
- svcs init - Register project and install hooks
- svcs remove - Unregister project and remove hooks  
- svcs status - Show project registration status
- svcs list - List all registered projects
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

import click
import yaml

# Import the git hook manager
from .git_hooks import GitHookManager


@click.group()
@click.version_option()
def main():
    """SVCS - Semantic Version Control System CLI."""
    pass


@main.command()
@click.option('--name', prompt='Project name', help='Human-readable name for the project')
@click.argument('path', default='.', type=click.Path(exists=True))
def init(name: str, path: str):
    """Initialize SVCS for a project (register and install hooks)."""
    path = os.path.abspath(path)
    
    # Check if it's a git repository
    if not (Path(path) / '.git').exists():
        click.echo(f"❌ Error: {path} is not a git repository", err=True)
        sys.exit(1)
    
    # Check if MCP server is available
    try:
        result = call_mcp_tool('register_project', {
            'path': path,
            'name': name
        })
        click.echo(result)
        
        # Install git hooks using the global hook manager
        hook_manager = GitHookManager()
        
        # Ensure global hook system is installed
        if not hook_manager.global_hook_script.exists():
            click.echo("🔧 Installing global SVCS hook system...")
            hook_manager.install_global_hooks()
        
        # Install hooks for this project
        click.echo("🔗 Installing git hooks...")
        if hook_manager.install_project_hooks(path):
            click.echo("✅ Git hooks installed successfully")
        else:
            click.echo("⚠️ Warning: Some git hooks failed to install", err=True)
        
        # Create local .svcs directory for project-specific config (optional)
        local_svcs = Path(path) / '.svcs'
        local_svcs.mkdir(exist_ok=True)
        
        # Create project config
        config = {
            'name': name,
            'path': path,
            'mcp_managed': True,
            'hooks_installed': True,
            'created_at': None  # Will be set by MCP server
        }
        
        with open(local_svcs / 'config.yaml', 'w') as f:
            yaml.dump(config, f)
        
        click.echo(f"📝 Created local config: {local_svcs / 'config.yaml'}")
        
        # Install git hooks
        try:
            hook_manager = GitHookManager(path)
            hook_manager.install_hooks()
            click.echo("✅ Git hooks installed")
        except Exception as e:
            click.echo(f"⚠️ Warning installing git hooks: {e}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('path', default='.', type=click.Path(exists=True))
def remove(path: str):
    """Remove SVCS from a project (unregister and remove hooks)."""
    path = os.path.abspath(path)
    
    try:
        result = call_mcp_tool('unregister_project', {
            'path': path
        })
        click.echo(result)
        
        # Remove local .svcs directory if it exists
        local_svcs = Path(path) / '.svcs'
        if local_svcs.exists():
            import shutil
            shutil.rmtree(local_svcs)
            click.echo(f"🗑️ Removed local config: {local_svcs}")
        
        # Uninstall git hooks
        hook_manager = GitHookManager()
        click.echo("🔗 Removing git hooks...")
        if hook_manager.uninstall_project_hooks(path):
            click.echo("✅ Git hooks removed successfully")
        else:
            click.echo("⚠️ Warning: Some git hooks failed to remove", err=True)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--quiet', is_flag=True, help='Suppress output for scripting')
def status(path: str, quiet: bool):
    """Show SVCS registration and git hook status for a project."""
    path = os.path.abspath(path)
    
    if not quiet:
        click.echo(f"📊 SVCS Status for: {path}")
        click.echo("=" * 50)
    
    # Check if it's a git repository
    if not (Path(path) / '.git').exists():
        if not quiet:
            click.echo(f"❌ Not a git repository")
        sys.exit(1)
    
    # Check registration status with MCP server
    try:
        result = call_mcp_tool('get_project_by_path', {'path': path})
        if "Error" in result:
            if not quiet:
                click.echo("📋 Registration: ❌ Not registered with SVCS")
            registered = False
        else:
            if not quiet:
                click.echo("📋 Registration: ✅ Registered with SVCS")
            registered = True
    except Exception as e:
        if not quiet:
            click.echo(f"📋 Registration: ❓ Cannot check (MCP server not available)")
        registered = False
    
    # Check git hook status
    hook_manager = GitHookManager()
    hook_status = hook_manager.get_project_hook_status(path)
    
    if not quiet:
        click.echo("\n🔗 Git Hooks:")
        for hook_name, status in hook_status.items():
            status_icon = {
                'svcs_installed': '✅',
                'not_installed': '❌',
                'custom_script': '⚠️',
                'other_symlink': '🔗'
            }.get(status, '❓')
            
            click.echo(f"  {hook_name}: {status_icon} {status}")
    
    # Check global hook system
    if not quiet:
        if hook_manager.global_hook_script.exists():
            click.echo(f"\n🌐 Global Hook: ✅ {hook_manager.global_hook_script}")
        else:
            click.echo(f"\n🌐 Global Hook: ❌ Not installed")
    
    # Exit code for scripting
    if registered and all(s == 'svcs_installed' for s in hook_status.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Not fully set up


@main.command()
def list():
    """List all SVCS registered projects."""
    try:
        result = call_mcp_tool('list_projects', {})
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command() 
@click.argument('path', default='.', type=click.Path(exists=True))
def stats(path: str):
    """Show semantic evolution statistics for a project."""
    path = os.path.abspath(path)
    
    try:
        result = call_mcp_tool('get_project_statistics', {
            'project_path': path
        })
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('query')
@click.option('--project', default='.', help='Project path')
def query(query: str, project: str):
    """Query semantic evolution using natural language."""
    project = os.path.abspath(project)
    
    try:
        result = call_mcp_tool('query_semantic_evolution', {
            'project_path': project,
            'query': query
        })
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


def call_mcp_tool(tool_name: str, args: Dict) -> str:
    """Call an MCP tool via the MCP server."""
    # For now, this is a placeholder that would connect to the actual MCP server
    # In production, this would use the MCP client library to communicate
    # with the running svcs-mcp-server
    
    # Simulate MCP server communication
    import tempfile
    import json
    
    # This is a temporary implementation - in production this would use
    # proper MCP client-server communication
    mcp_request = {
        "tool": tool_name,
        "arguments": args
    }
    
    # For demo purposes, return a mock response
    if tool_name == "register_project":
        return f"✅ Successfully registered project '{args['name']}'\nProject ID: mock-id-123\nGit hooks installed in: {args['path']}/.git/hooks/"
    elif tool_name == "unregister_project":
        return f"✅ Successfully unregistered project: {args['path']}\nGit hooks removed and data cleaned up"
    elif tool_name == "list_projects":
        return "📋 SVCS Registered Projects (0):\n\nNo projects registered with SVCS"
    elif tool_name == "get_project_statistics":
        return f"📊 Statistics for project:\n\nTotal semantic events: 0\nRecent events (7 days): 0\n\nNo semantic events recorded yet."
    else:
        return f"🚧 Tool '{tool_name}' not yet implemented in CLI mock mode"


if __name__ == '__main__':
    main()
