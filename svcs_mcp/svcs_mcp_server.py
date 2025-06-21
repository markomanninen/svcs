#!/usr/bin/env python3
"""
SVCS MCP Server - Model Context Protocol server for semantic code evolution analysis.

This server provides MCP tools for managing and querying semantic code evolution
across multiple projects from a centralized service.
"""

import asyncio
import json
import logging
import os
import sqlite3
import subprocess
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("svcs-mcp-server")

# Global SVCS directory
SVCS_HOME = Path.home() / ".svcs"
GLOBAL_DB = SVCS_HOME / "global.db"
CONFIG_FILE = SVCS_HOME / "config.yaml"
HOOKS_DIR = SVCS_HOME / "hooks"
PROJECTS_DIR = SVCS_HOME / "projects"


class GlobalSVCSDatabase:
    """Manages the global SVCS database with multi-project support."""
    
    def __init__(self, db_path: Path = GLOBAL_DB):
        self.db_path = db_path
        self.ensure_directory()
        self.init_schema()
    
    def ensure_directory(self):
        """Ensure the SVCS directory structure exists."""
        SVCS_HOME.mkdir(exist_ok=True)
        HOOKS_DIR.mkdir(exist_ok=True)
        PROJECTS_DIR.mkdir(exist_ok=True)
        (SVCS_HOME / "logs").mkdir(exist_ok=True)
        (SVCS_HOME / "cache").mkdir(exist_ok=True)
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_schema(self):
        """Initialize the global database schema."""
        with self.get_connection() as conn:
            # Projects table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    created_at INTEGER NOT NULL,
                    last_analyzed INTEGER,
                    status TEXT DEFAULT 'active',
                    config TEXT DEFAULT '{}'
                )
            """)
            
            # Commits table with project_id
            conn.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    commit_hash TEXT,
                    project_id TEXT NOT NULL,
                    author TEXT,
                    timestamp INTEGER,
                    message TEXT,
                    PRIMARY KEY (commit_hash, project_id),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)
            
            # Semantic events table with project_id
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_events (
                    event_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    commit_hash TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    node_id TEXT,
                    location TEXT,
                    details TEXT,
                    layer TEXT,
                    layer_description TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    impact TEXT,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)
            
            conn.commit()
    
    def register_project(self, name: str, path: str) -> str:
        """Register a new project and return project_id."""
        project_id = str(uuid.uuid4())
        created_at = int(datetime.now().timestamp())
        
        # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
        path = str(Path(path).resolve())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO projects (project_id, name, path, created_at)
                VALUES (?, ?, ?, ?)
            """, (project_id, name, path, created_at))
            conn.commit()
        
        return project_id
    
    def unregister_project(self, path: str) -> bool:
        """Unregister a project and cleanup its data."""
        with self.get_connection() as conn:
            # Get project_id first
            cursor = conn.execute(
                "SELECT project_id FROM projects WHERE path = ?", (path,)
            )
            result = cursor.fetchone()
            
            if not result:
                return False
            
            project_id = result[0]
            
            # Delete semantic events
            conn.execute(
                "DELETE FROM semantic_events WHERE project_id = ?", (project_id,)
            )
            
            # Delete commits  
            conn.execute(
                "DELETE FROM commits WHERE project_id = ?", (project_id,)
            )
            
            # Delete project
            conn.execute(
                "DELETE FROM projects WHERE project_id = ?", (project_id,)
            )
            
            conn.commit()
        
        return True
    
    def get_project_by_path(self, path: str) -> Optional[Dict]:
        """Get project info by path."""
        # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
        path = str(Path(path).resolve())
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT project_id, name, path, created_at, last_analyzed, status
                FROM projects WHERE path = ?
            """, (path,))
            
            result = cursor.fetchone()
            if result:
                return {
                    "project_id": result[0],
                    "name": result[1], 
                    "path": result[2],
                    "created_at": result[3],
                    "last_analyzed": result[4],
                    "status": result[5]
                }
        return None
    
    def list_projects(self) -> List[Dict]:
        """List all registered projects."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT project_id, name, path, created_at, last_analyzed, status
                FROM projects ORDER BY created_at DESC
            """)
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    "project_id": row[0],
                    "name": row[1],
                    "path": row[2], 
                    "created_at": row[3],
                    "last_analyzed": row[4],
                    "status": row[5]
                })
            
            return projects


class ProjectManager:
    """Manages git hooks and project registration."""
    
    def __init__(self, db: GlobalSVCSDatabase):
        self.db = db
        self.hook_script = HOOKS_DIR / "svcs-hook"
        self.create_global_hook()
    
    def create_global_hook(self):
        """Create the global git hook script."""
        hook_content = '''#!/bin/bash
# SVCS Global Git Hook
# This script is managed by SVCS MCP Server

# Get the current repository path
REPO_PATH=$(git rev-parse --show-toplevel)

# Call the SVCS MCP server to process this commit
python3 -c "
import sys
sys.path.append('{}')
from svcs_mcp_server import process_commit
process_commit('$REPO_PATH')
" 2>/dev/null || true
'''.format(str(Path(__file__).parent))

        self.hook_script.write_text(hook_content)
        self.hook_script.chmod(0o755)
    
    def install_hooks(self, project_path: str) -> bool:
        """Install git hooks for a project."""
        git_hooks_dir = Path(project_path) / ".git" / "hooks"
        
        if not git_hooks_dir.exists():
            return False
        
        # Only install post-commit hook to avoid double analysis
        hook_name = "post-commit"
        hook_path = git_hooks_dir / hook_name
        
        # Remove existing hook if it exists
        if hook_path.exists():
            hook_path.unlink()
        
        # Create symlink to global hook
        hook_path.symlink_to(self.hook_script)
        
        return True
    
    def remove_hooks(self, project_path: str) -> bool:
        """Remove git hooks for a project."""
        git_hooks_dir = Path(project_path) / ".git" / "hooks"
        
        if not git_hooks_dir.exists():
            return False
        
        # Remove SVCS hooks (check both post-commit and any legacy hooks)
        for hook_name in ["post-commit", "post-merge", "pre-commit"]:
            hook_path = git_hooks_dir / hook_name
            
            # Only remove if it's pointing to our global hook
            if hook_path.is_symlink() and hook_path.resolve() == self.hook_script:
                hook_path.unlink()
        
        return True


class SVCSQueryEngine:
    """Handles semantic evolution queries across projects."""
    
    def __init__(self, db: GlobalSVCSDatabase):
        self.db = db
    
    def query_project_evolution(self, project_id: str, query: str) -> Dict:
        """Query semantic evolution for a specific project."""
        # This would integrate with the existing SVCS conversational interface
        # For now, return a placeholder
        return {
            "project_id": project_id,
            "query": query,
            "results": [],
            "message": "Semantic evolution query functionality coming soon"
        }
    
    def get_project_statistics(self, project_id: str) -> Dict:
        """Get statistics for a project."""
        with self.db.get_connection() as conn:
            # Count events by type
            cursor = conn.execute("""
                SELECT event_type, COUNT(*) as count
                FROM semantic_events 
                WHERE project_id = ?
                GROUP BY event_type
                ORDER BY count DESC
            """, (project_id,))
            
            event_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get total events and recent activity
            cursor = conn.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN created_at > ? THEN 1 END) as recent
                FROM semantic_events 
                WHERE project_id = ?
            """, (int((datetime.now() - timedelta(days=7)).timestamp()), project_id))
            
            total, recent = cursor.fetchone()
            
            return {
                "project_id": project_id,
                "total_events": total,
                "recent_events_7days": recent,
                "event_types": event_stats
            }


# Initialize components
db = GlobalSVCSDatabase()
project_manager = ProjectManager(db)
query_engine = SVCSQueryEngine(db)

# Create MCP server
server = Server("svcs-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available SVCS MCP tools."""
    return [
        types.Tool(
            name="register_project",
            description="Register a project for SVCS semantic analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the git repository"
                    },
                    "name": {
                        "type": "string", 
                        "description": "Human-readable name for the project"
                    }
                },
                "required": ["path", "name"]
            }
        ),
        types.Tool(
            name="unregister_project",
            description="Unregister a project and remove SVCS tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the git repository"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="list_projects",
            description="List all registered SVCS projects",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_project_statistics",
            description="Get semantic evolution statistics for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project"
                    }
                },
                "required": ["project_path"]
            }
        ),
        types.Tool(
            name="query_semantic_evolution",
            description="Query semantic code evolution using natural language",
            inputSchema={
                "type": "object", 
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project"
                    },
                    "query": {
                        "type": "string",
                        "description": "Natural language query about code evolution"
                    }
                },
                "required": ["project_path", "query"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
    
    try:
        if name == "register_project":
            path = arguments["path"]
            project_name = arguments["name"]
            
            # Check if already registered
            existing = db.get_project_by_path(path)
            if existing:
                return [types.TextContent(
                    type="text",
                    text=f"Project already registered: {existing['name']}"
                )]
            
            # Check if it's a git repository, if not initialize it
            git_dir = Path(path) / '.git'
            git_init_msg = ""
            
            if not git_dir.exists():
                try:
                    result = subprocess.run(['git', 'init'], cwd=path, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        git_init_msg = f"📁 Directory was not a git repository. Git initialized in {path}\n"
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"❌ Error initializing git: {result.stderr.strip() or 'Git init failed'}"
                        )]
                except FileNotFoundError:
                    return [types.TextContent(
                        type="text",
                        text="❌ Error: git command not found. Please install git first."
                    )]
                except subprocess.TimeoutExpired:
                    return [types.TextContent(
                        type="text",
                        text="❌ Error: git init timed out"
                    )]
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"❌ Error initializing git: {str(e)}"
                    )]
            
            # Register project
            project_id = db.register_project(project_name, path)
            
            # Install git hooks
            success = project_manager.install_hooks(path)
            
            result = git_init_msg
            if success:
                result += f"✅ Project '{project_name}' registered!\n"
                result += f"📝 Project ID: {project_id[:8]}...\n"
                result += f"📁 Path: {path}\n"
                result += f"🔗 Git hooks installed successfully"
            else:
                result += f"⚠️ Project registered but failed to install git hooks\n"
                result += f"Please ensure {path} is a valid git repository"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "unregister_project":
            path = arguments["path"]
            
            # Remove hooks first
            project_manager.remove_hooks(path)
            
            # Unregister project
            success = db.unregister_project(path)
            
            if success:
                result = f"✅ Successfully unregistered project: {path}\n"
                result += "Git hooks removed and data cleaned up"
            else:
                result = f"❌ Project not found: {path}"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "list_projects":
            projects = db.list_projects()
            
            if not projects:
                return [types.TextContent(
                    type="text",
                    text="No projects registered with SVCS"
                )]
            
            result = f"📋 SVCS Registered Projects ({len(projects)}):\n\n"
            
            for project in projects:
                created = datetime.fromtimestamp(project['created_at']).strftime('%Y-%m-%d')
                last_analyzed = "Never"
                if project['last_analyzed']:
                    last_analyzed = datetime.fromtimestamp(project['last_analyzed']).strftime('%Y-%m-%d')
                
                result += f"• **{project['name']}** ({project['status']})\n"
                result += f"  Path: {project['path']}\n"
                result += f"  Created: {created}, Last analyzed: {last_analyzed}\n\n"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "get_project_statistics":
            project_path = arguments["project_path"]
            project = db.get_project_by_path(project_path)
            
            if not project:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Project not registered: {project_path}"
                )]
            
            stats = query_engine.get_project_statistics(project['project_id'])
            
            result = f"📊 Statistics for {project['name']}:\n\n"
            result += f"Total semantic events: {stats['total_events']}\n"
            result += f"Recent events (7 days): {stats['recent_events_7days']}\n\n"
            
            if stats['event_types']:
                result += "Event types breakdown:\n"
                for event_type, count in stats['event_types'].items():
                    result += f"  • {event_type}: {count}\n"
            else:
                result += "No semantic events recorded yet.\n"
            
            return [types.TextContent(type="text", text=result)]
        
        elif name == "query_semantic_evolution":
            project_path = arguments["project_path"]
            query = arguments["query"]
            
            project = db.get_project_by_path(project_path)
            
            if not project:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Project not registered: {project_path}"
                )]
            
            # For now, return a placeholder
            result = f"🔍 Query: '{query}'\n"
            result += f"Project: {project['name']}\n\n"
            result += "🚧 Semantic evolution querying will be integrated with the existing SVCS conversational interface in the next phase."
            
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]


def process_commit(repo_path: str):
    """Process a git commit for semantic analysis."""
    # This would be called by the git hook
    # For now, just log that a commit was processed
    logger.info(f"Processing commit in: {repo_path}")
    
    # TODO: Integrate with existing SVCS analysis logic
    # 1. Get project_id from repo_path
    # 2. Run semantic analysis on latest commit
    # 3. Store results in global database with project_id


async def main():
    """Main entry point for the MCP server."""
    # Ensure SVCS directory structure exists
    db.ensure_directory()
    
    logger.info("Starting SVCS MCP Server...")
    logger.info(f"Global database: {GLOBAL_DB}")
    logger.info(f"Global hooks: {HOOKS_DIR}")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="svcs-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
