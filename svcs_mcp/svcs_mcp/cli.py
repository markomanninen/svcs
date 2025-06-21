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
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import click
import yaml

# Import the git hook manager
try:
    from .git_hooks import GitHookManager
except ImportError:
    # Handle direct execution
    import sys
    sys.path.append(os.path.dirname(__file__))
    from git_hooks import GitHookManager

# Global SVCS directory and database
SVCS_HOME = Path.home() / ".svcs"
GLOBAL_DB = SVCS_HOME / "global.db"


class SVCSDatabase:
    """Direct database interface for CLI to access SVCS data."""
    
    def __init__(self, db_path: Path = GLOBAL_DB):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection."""
        if not self.db_path.exists():
            return None
        return sqlite3.connect(str(self.db_path))
    
    def register_project(self, name: str, path: str) -> str:
        """Register a new project."""
        try:
            conn = self.get_connection()
            if not conn:
                return "❌ Error: SVCS database not found. Is the MCP server initialized?"
            
            project_id = str(uuid.uuid4())
            created_at = int(datetime.now().timestamp())
            
            # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
            path = str(Path(path).resolve())
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (project_id, name, path, created_at, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (project_id, name, path, created_at))
            conn.commit()
            conn.close()
            
            return f"✅ Successfully registered project '{name}'\nProject ID: {project_id[:8]}...\nPath: {path}"
        except Exception as e:
            return f"❌ Error registering project: {str(e)}"
    
    def unregister_project(self, path: str) -> str:
        """Unregister a project."""
        try:
            conn = self.get_connection()
            if not conn:
                return "❌ Error: SVCS database not found"
            
            cursor = conn.cursor()
            cursor.execute("UPDATE projects SET status = 'inactive' WHERE path = ?", (path,))
            if cursor.rowcount == 0:
                return f"❌ Error: Project not found: {path}"
            
            conn.commit()
            conn.close()
            return f"✅ Successfully unregistered project: {path}"
        except Exception as e:
            return f"❌ Error unregistering project: {str(e)}"
    
    def list_projects(self) -> str:
        """List all registered projects."""
        try:
            conn = self.get_connection()
            if not conn:
                return "📋 SVCS Registered Projects (0):\n\nNo projects registered with SVCS\n(SVCS database not found - is MCP server initialized?)"
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, project_id, path, created_at 
                FROM projects 
                WHERE status = 'active' 
                ORDER BY created_at DESC
            """)
            projects = cursor.fetchall()
            conn.close()
            
            if not projects:
                return "📋 SVCS Registered Projects (0):\n\nNo projects registered with SVCS"
            
            result = f"📋 SVCS Registered Projects ({len(projects)}):\n\n"
            for name, project_id, path, created_at in projects:
                result += f"• **{name}**\n"
                result += f"  - ID: `{project_id[:8]}...`\n"
                result += f"  - Path: `{path}`\n"
                result += f"  - Created: {datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            return result
        except Exception as e:
            return f"❌ Error listing projects: {str(e)}"
    
    def get_project_by_path(self, path: str) -> Optional[Dict]:
        """Get project information by path."""
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
            path = str(Path(path).resolve())
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT project_id, name, path, created_at 
                FROM projects 
                WHERE path = ? AND status = 'active'
            """, (path,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'path': row[2],
                    'created_at': row[3]
                }
            return None
        except Exception:
            return None
    
    def get_project_statistics(self, project_path: str) -> str:
        """Get project statistics."""
        try:
            conn = self.get_connection()
            if not conn:
                return "❌ Error: SVCS database not found"
            
            # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
            project_path = str(Path(project_path).resolve())
            
            # Get project ID
            cursor = conn.cursor()
            cursor.execute("SELECT project_id FROM projects WHERE path = ? AND status = 'active'", (project_path,))
            project_row = cursor.fetchone()
            if not project_row:
                return f"❌ Error: Project not registered: {project_path}"
            
            project_id = project_row[0]
            
            # Count total events
            cursor.execute("SELECT COUNT(*) FROM semantic_events WHERE project_id = ?", (project_id,))
            total_events = cursor.fetchone()[0]
            
            # Count recent events (last 7 days)
            seven_days_ago = int((datetime.now() - timedelta(days=7)).timestamp())
            cursor.execute("""
                SELECT COUNT(*) FROM semantic_events 
                WHERE project_id = ? AND created_at > ?
            """, (project_id, seven_days_ago))
            recent_events = cursor.fetchone()[0]
            
            conn.close()
            
            result = f"📊 Statistics for project: {project_path}\n\n"
            result += f"Total semantic events: {total_events}\n"
            result += f"Recent events (7 days): {recent_events}\n"
            
            if total_events == 0:
                result += "\nNo semantic events recorded yet."
            
            return result
        except Exception as e:
            return f"❌ Error getting statistics: {str(e)}"


# Global database instance
db = SVCSDatabase()


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
    
    # Check if it's a git repository, if not initialize it
    git_dir = Path(path) / '.git'
    if not git_dir.exists():
        click.echo(f"📁 Directory is not a git repository. Initializing git...")
        try:
            result = subprocess.run(['git', 'init'], cwd=path, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo(f"✅ Git repository initialized in {path}")
            else:
                click.echo(f"❌ Error initializing git: {result.stderr}", err=True)
                sys.exit(1)
        except FileNotFoundError:
            click.echo("❌ Error: git command not found. Please install git first.", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error initializing git: {e}", err=True)
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
            'path': path
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


@main.command()
@click.argument('project_path', default='.', type=click.Path(exists=True))
def analyze_commit(project_path: str):
    """Analyze the latest commit for semantic changes."""
    path = os.path.abspath(project_path)
    
    try:
        # Import semantic analyzer
        from .semantic_analyzer import GlobalSemanticAnalyzer
        
        analyzer = GlobalSemanticAnalyzer()
        result = analyzer.analyze_commit(path)
        
        if "error" in result:
            click.echo(f"❌ Error: {result['error']}", err=True)
            sys.exit(1)
        else:
            click.echo(f"🔍 {result['message']}")
            if result.get('events_stored', 0) > 0:
                click.echo(f"✅ Stored {result['events_stored']} semantic events")
                click.echo(f"📊 Project: {result['project_id'][:8]}...")
                click.echo(f"📝 Commit: {result['commit_hash'][:8]}...")
            
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


@main.command() 
@click.argument('project_path', default='.', type=click.Path(exists=True))
def analyze_pre_commit(project_path: str):
    """Analyze staged changes before commit."""
    click.echo("🔍 SVCS: Pre-commit analysis (placeholder)")
    # TODO: Implement pre-commit analysis


@main.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('hook_type')
@click.argument('args', nargs=-1)
def log_hook_event(project_path: str, hook_type: str, args):
    """Log a git hook event."""
    click.echo(f"📝 SVCS: Logged {hook_type} event for {project_path}")


def call_mcp_tool(tool_name: str, args: Dict) -> str:
    """Call MCP functionality via direct database access."""
    
    # Route to appropriate database method
    if tool_name == "register_project":
        return db.register_project(args['name'], args['path'])
    elif tool_name == "unregister_project":
        return db.unregister_project(args['path'])
    elif tool_name == "list_projects":
        return db.list_projects()
    elif tool_name == "get_project_by_path":
        project = db.get_project_by_path(args['path'])
        if project:
            return f"Project found: {project['name']}"
        else:
            return "Error: Project not registered"
    elif tool_name == "get_project_statistics":
        return db.get_project_statistics(args['path'])
    elif tool_name == "query_semantic_evolution":
        return f"� Semantic evolution query: {args['query']}\n\n🚧 Natural language querying will be available when MCP server is running."
    else:
        return f"🚧 Tool '{tool_name}' not yet implemented"


if __name__ == '__main__':
    main()
