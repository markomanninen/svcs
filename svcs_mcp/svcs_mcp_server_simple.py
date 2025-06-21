#!/usr/bin/env python3
"""
SVCS MCP Server - Simplified version without MCP dependencies for demonstration.

This version shows the core architecture and database functionality.
In production, this would include the full MCP integration.
"""

import asyncio
import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


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
from svcs_mcp_server_simple import process_commit
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
        
        # Create symlinks to global hook
        for hook_name in ["post-commit", "post-merge"]:
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
        
        # Remove SVCS hooks
        for hook_name in ["post-commit", "post-merge"]:
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
        return {
            "project_id": project_id,
            "query": query,
            "results": [],
            "message": "Evolution querying ready for integration with existing SVCS"
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


def process_commit(repo_path: str):
    """Process a git commit for semantic analysis."""
    logger.info(f"Processing commit in: {repo_path}")
    
    # This would integrate with existing SVCS analysis logic
    # 1. Get project_id from repo_path
    # 2. Run semantic analysis on latest commit
    # 3. Store results in global database with project_id


# Simple demonstration function
def demo_mcp_functionality():
    """Demonstrate MCP server functionality without MCP dependencies."""
    print("🚀 SVCS MCP Server - Core Functionality Demo")
    print("=" * 60)
    
    # Initialize components
    db = GlobalSVCSDatabase()
    project_manager = ProjectManager(db)
    query_engine = SVCSQueryEngine(db)
    
    print("✅ Initialized all core components")
    print(f"📁 Global SVCS directory: {SVCS_HOME}")
    print(f"🗄️ Global database: {GLOBAL_DB}")
    print(f"🔗 Global hook script: {project_manager.hook_script}")
    
    return {
        "db": db,
        "project_manager": project_manager,
        "query_engine": query_engine
    }


if __name__ == "__main__":
    demo_mcp_functionality()
