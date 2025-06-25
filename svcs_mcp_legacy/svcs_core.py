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
                    created_at INTEGER,
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
        """Register a new project or reactivate an existing one."""
        # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
        path = str(Path(path).resolve())
        
        with self.get_connection() as conn:
            # Check if project already exists
            cursor = conn.execute(
                "SELECT project_id, name, status FROM projects WHERE path = ?", (path,)
            )
            result = cursor.fetchone()
            
            if result:
                project_id, existing_name, status = result
                
                if status == 'active':
                    return f"✅ Project '{existing_name}' is already active at {path}"
                else:
                    # Reactivate inactive project
                    conn.execute(
                        "UPDATE projects SET status = 'active', name = ? WHERE path = ?",
                        (name, path)
                    )
                    conn.commit()
                    return f"✅ Reactivated project '{name}' (was: '{existing_name}') at {path}"
            else:
                # Create new project
                project_id = str(uuid.uuid4())
                created_at = int(datetime.now().timestamp())
                
                conn.execute("""
                    INSERT INTO projects (project_id, name, path, created_at, status)
                    VALUES (?, ?, ?, ?, 'active')
                """, (project_id, name, path, created_at))
                conn.commit()
                return f"✅ Successfully registered new project '{name}' at {path}"
    
    def unregister_project(self, path: str) -> str:
        """Unregister a project (soft delete - mark as inactive but keep data)."""
        # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
        path = str(Path(path).resolve())
        
        with self.get_connection() as conn:
            # Check if project exists and is active
            cursor = conn.execute(
                "SELECT project_id, name, status FROM projects WHERE path = ?", (path,)
            )
            result = cursor.fetchone()
            
            if not result:
                return f"❌ Project not found: {path}"
            
            project_id, name, current_status = result
            
            if current_status == 'inactive':
                return f"⚠️ Project '{name}' is already inactive"
            
            # Mark project as inactive (soft delete)
            conn.execute(
                "UPDATE projects SET status = 'inactive' WHERE project_id = ?", (project_id,)
            )
            
            conn.commit()
        
        return f"✅ Project '{name}' unregistered (marked as inactive). Data preserved for recovery."

    def purge_project(self, path: str) -> str:
        """Completely remove a project and all its data (hard delete)."""
        # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
        path = str(Path(path).resolve())
        
        with self.get_connection() as conn:
            # Get project info first
            cursor = conn.execute(
                "SELECT project_id, name FROM projects WHERE path = ?", (path,)
            )
            result = cursor.fetchone()
            
            if not result:
                return f"❌ Project not found: {path}"
            
            project_id, name = result
            
            # Count data before deletion for feedback
            cursor.execute("SELECT COUNT(*) FROM semantic_events WHERE project_id = ?", (project_id,))
            event_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM commits WHERE project_id = ?", (project_id,))
            commit_count = cursor.fetchone()[0]
            
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
        
        return f"🗑️ Project '{name}' completely purged ({event_count} events, {commit_count} commits deleted)"
    
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
    
    def get_project_id_by_path(self, path: str) -> Optional[str]:
        """Get project ID by path."""
        # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
        path = str(Path(path).resolve())
        
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT project_id FROM projects WHERE path = ? AND status = 'active'", (path,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project information by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT project_id, name, path, created_at, status 
                FROM projects WHERE project_id = ?
            """, (project_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'project_id': result[0],
                    'name': result[1],
                    'path': result[2],
                    'created_at': result[3],
                    'status': result[4]
                }
            return None

        return True
    
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
    
    def query_semantic_events(self, project_id: Optional[str] = None, 
                             event_type: Optional[str] = None, 
                             limit: int = 10) -> List[Dict[str, Any]]:
        """Query semantic events with optional filters."""
        query = """
            SELECT 
                se.event_id,
                se.project_id,
                se.commit_hash,
                se.event_type,
                se.node_id,
                se.location,
                se.details,
                se.layer,
                se.confidence,
                se.created_at,
                c.author,
                c.timestamp,
                c.message,
                p.name as project_name
            FROM semantic_events se
            LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
            LEFT JOIN projects p ON se.project_id = p.project_id
            WHERE 1=1
        """
        
        params = []
        
        if project_id:
            query += " AND se.project_id = ?"
            params.append(project_id)
        
        if event_type:
            query += " AND se.event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY se.created_at DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                results.append(event)
        
        return results
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a specific project."""
        with self.get_connection() as conn:
            # Total events
            cursor = conn.execute(
                "SELECT COUNT(*) FROM semantic_events WHERE project_id = ?",
                (project_id,)
            )
            total_events = cursor.fetchone()[0]
            
            # Event types breakdown
            cursor = conn.execute("""
                SELECT event_type, COUNT(*) as count 
                FROM semantic_events 
                WHERE project_id = ? 
                GROUP BY event_type 
                ORDER BY count DESC
            """, (project_id,))
            event_types = dict(cursor.fetchall())
            
            # Layer breakdown
            cursor = conn.execute("""
                SELECT layer, COUNT(*) as count 
                FROM semantic_events 
                WHERE project_id = ? 
                GROUP BY layer 
                ORDER BY count DESC
            """, (project_id,))
            layers = dict(cursor.fetchall())
            
            # Recent commits
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT commit_hash) 
                FROM semantic_events 
                WHERE project_id = ?
            """, (project_id,))
            total_commits = cursor.fetchone()[0]
            
            return {
                "total_events": total_events,
                "total_commits": total_commits,
                "event_types": event_types,
                "layers": layers
            }

    def prune_orphaned_data(self, project_path: str = None) -> Dict[str, Any]:
        """Remove data for commits that no longer exist in git history."""
        import subprocess
        import os
        from pathlib import Path
        
        try:
            if project_path:
                # Get project ID first
                project_id = self.get_project_id_by_path(project_path)
                if not project_id:
                    return {"error": f"Project not registered: {project_path}"}
                
                # Change to project directory to run git commands
                original_cwd = os.getcwd()
                try:
                    os.chdir(project_path)
                    
                    # Get valid commit hashes from git
                    cmd = ["git", "log", "--format=%H"]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    git_hashes = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
                    
                    # Get commit hashes from database for this project
                    with self.get_connection() as conn:
                        db_hashes = set()
                        cursor = conn.execute(
                            "SELECT DISTINCT commit_hash FROM semantic_events WHERE project_id = ?",
                            (project_id,)
                        )
                        for row in cursor.fetchall():
                            db_hashes.add(row[0])
                        
                        # Find orphaned hashes
                        orphaned_hashes = db_hashes - git_hashes
                        
                        if not orphaned_hashes:
                            return {"message": "No orphaned data found", "pruned_count": 0}
                        
                        # Remove orphaned data
                        pruned_count = 0
                        for commit_hash in orphaned_hashes:
                            cursor = conn.execute(
                                "DELETE FROM semantic_events WHERE project_id = ? AND commit_hash = ?",
                                (project_id, commit_hash)
                            )
                            pruned_count += cursor.rowcount
                        
                        conn.commit()
                        
                        return {
                            "message": f"Successfully pruned data for {len(orphaned_hashes)} orphaned commit(s)",
                            "pruned_count": len(orphaned_hashes),
                            "deleted_events": pruned_count
                        }
                        
                finally:
                    os.chdir(original_cwd)
                    
            else:
                # Global prune across all projects
                with self.get_connection() as conn:
                    # Get all projects
                    projects = conn.execute("SELECT project_id, path FROM projects").fetchall()
                    
                    total_pruned = 0
                    total_deleted_events = 0
                    project_results = []
                    
                    for project_id, path in projects:
                        if not Path(path).exists():
                            continue
                            
                        try:
                            original_cwd = os.getcwd()
                            os.chdir(path)
                            
                            # Get valid commit hashes from git
                            cmd = ["git", "log", "--format=%H"]
                            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                            git_hashes = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
                            
                            # Get commit hashes from database for this project
                            db_hashes = set()
                            cursor = conn.execute(
                                "SELECT DISTINCT commit_hash FROM semantic_events WHERE project_id = ?",
                                (project_id,)
                            )
                            for row in cursor.fetchall():
                                db_hashes.add(row[0])
                            
                            # Find and remove orphaned hashes
                            orphaned_hashes = db_hashes - git_hashes
                            deleted_events = 0
                            
                            for commit_hash in orphaned_hashes:
                                cursor = conn.execute(
                                    "DELETE FROM semantic_events WHERE project_id = ? AND commit_hash = ?",
                                    (project_id, commit_hash)
                                )
                                deleted_events += cursor.rowcount
                            
                            if orphaned_hashes:
                                total_pruned += len(orphaned_hashes)
                                total_deleted_events += deleted_events
                                project_results.append({
                                    "project_id": project_id,
                                    "path": path,
                                    "pruned_commits": len(orphaned_hashes),
                                    "deleted_events": deleted_events
                                })
                                
                        except subprocess.CalledProcessError:
                            # Skip projects where git commands fail
                            continue
                        finally:
                            os.chdir(original_cwd)
                    
                    conn.commit()
                    
                    return {
                        "message": f"Global prune completed. Pruned {total_pruned} orphaned commits across {len(project_results)} projects",
                        "total_pruned_commits": total_pruned,
                        "total_deleted_events": total_deleted_events,
                        "project_results": project_results
                    }
                    
        except Exception as e:
            return {"error": f"Prune operation failed: {str(e)}"}


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
from svcs_core import process_commit
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
        
        # Only install post-commit hook (not pre-commit to avoid double analysis)
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
        
        # Remove SVCS hooks
        for hook_name in ["post-commit", "pre-commit"]:  # Remove both in case of old installations
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
    
    def query_semantic_events(self, project_id: Optional[str] = None, 
                             event_type: Optional[str] = None, 
                             limit: int = 10) -> List[Dict[str, Any]]:
        """Query semantic events with optional filters."""
        query = """
            SELECT 
                se.event_id,
                se.project_id,
                se.commit_hash,
                se.event_type,
                se.node_id,
                se.location,
                se.details,
                se.layer,
                se.confidence,
                se.created_at,
                c.author,
                c.timestamp,
                c.message,
                p.name as project_name
            FROM semantic_events se
            LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
            LEFT JOIN projects p ON se.project_id = p.project_id
            WHERE 1=1
        """
        
        params = []
        
        if project_id:
            query += " AND se.project_id = ?"
            params.append(project_id)
        
        if event_type:
            query += " AND se.event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY se.created_at DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                results.append(event)
        
        return results
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a specific project."""
        with self.get_connection() as conn:
            # Total events
            cursor = conn.execute(
                "SELECT COUNT(*) FROM semantic_events WHERE project_id = ?",
                (project_id,)
            )
            total_events = cursor.fetchone()[0]
            
            # Event types breakdown
            cursor = conn.execute("""
                SELECT event_type, COUNT(*) as count 
                FROM semantic_events 
                WHERE project_id = ? 
                GROUP BY event_type 
                ORDER BY count DESC
            """, (project_id,))
            event_types = dict(cursor.fetchall())
            
            # Layer breakdown
            cursor = conn.execute("""
                SELECT layer, COUNT(*) as count 
                FROM semantic_events 
                WHERE project_id = ? 
                GROUP BY layer 
                ORDER BY count DESC
            """, (project_id,))
            layers = dict(cursor.fetchall())
            
            # Recent commits
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT commit_hash) 
                FROM semantic_events 
                WHERE project_id = ?
            """, (project_id,))
            total_commits = cursor.fetchone()[0]
            
            return {
                "total_events": total_events,
                "total_commits": total_commits,
                "event_types": event_types,
                "layers": layers
            }
    
    def search_events_advanced(self, project_path: str, **kwargs) -> str:
        """Advanced search with comprehensive filtering options."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Build query with filters
            query = "SELECT * FROM semantic_events WHERE project_id = ?"
            params = [project_id]
            
            # Apply filters
            if kwargs.get('event_types'):
                placeholders = ','.join(['?' for _ in kwargs['event_types']])
                query += f" AND event_type IN ({placeholders})"
                params.extend(kwargs['event_types'])
                
            if kwargs.get('since_date'):
                # Parse date - could be "YYYY-MM-DD" or "N days ago"
                since_date = kwargs['since_date']
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    # Parse YYYY-MM-DD format
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND created_at > ?"
                params.append(timestamp)
            
            if kwargs.get('location_pattern'):
                query += " AND location LIKE ?"
                params.append(f"%{kwargs['location_pattern']}%")
                
            if kwargs.get('min_confidence'):
                query += " AND confidence >= ?"
                params.append(kwargs['min_confidence'])
            
            # Order and limit
            order_by = kwargs.get('order_by', 'created_at')
            order_desc = kwargs.get('order_desc', True)
            limit = kwargs.get('limit', 20)
            
            query += f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'} LIMIT ?"
            params.append(limit)
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return "🔍 Advanced Search Results: No events found matching the criteria"
            
            result = f"🔍 Advanced Search Results ({len(events)} events):\n\n"
            for event in events:
                result += f"• **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"  - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                if event[6]:  # details
                    result += f"  - Details: {event[6]}\n"
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error in advanced search: {str(e)}"
    
    def get_recent_activity(self, project_path: str, **kwargs) -> str:
        """Get recent project activity with filtering options."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Get parameters
            days = kwargs.get('days', 7)
            limit = kwargs.get('limit', 15)
            layers = kwargs.get('layers', [])
            
            # Build query
            since_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
            query = "SELECT * FROM semantic_events WHERE project_id = ? AND created_at > ?"
            params = [project_id, since_timestamp]
                
            if layers:
                placeholders = ','.join(['?' for _ in layers])
                query += f" AND layer IN ({placeholders})"
                params.extend(layers)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return f"📈 Recent Activity (last {days} days): No activity found"
            
            result = f"📈 Recent Activity (last {days} days, {len(events)} events):\n\n"
            for event in events:
                result += f"• **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"  - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting recent activity: {str(e)}"
    
    def search_semantic_patterns(self, project_path: str, pattern_type: str, **kwargs) -> str:
        """Search for specific AI-detected semantic patterns."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Get parameters
            min_confidence = kwargs.get('min_confidence', 0.7)
            limit = kwargs.get('limit', 10)
            since_date = kwargs.get('since_date')
            
            # Build query to search for pattern in description or event_type
            query = """
                SELECT * FROM semantic_events 
                WHERE project_id = ? 
                AND (event_type LIKE ? OR details LIKE ?)
                AND confidence >= ?
            """
            params = [project_id, f"%{pattern_type}%", f"%{pattern_type}%", min_confidence]
            
            if since_date:
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND created_at > ?"
                params.append(timestamp)
            
            query += " ORDER BY confidence DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return f"🔍 Semantic Pattern Search: No '{pattern_type}' patterns found"
            
            result = f"🔍 Semantic Pattern Search: '{pattern_type}' ({len(events)} matches):\n\n"
            for event in events:
                result += f"• **{event[3]}** (confidence: {event[9]:.2f})\n"  # event_type, confidence
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"  - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                if event[6]:  # details
                    result += f"  - Details: {event[6]}\n"
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error searching semantic patterns: {str(e)}"
    
    def get_filtered_evolution(self, project_path: str, node_id: str, **kwargs) -> str:
        """Get filtered evolution history for a specific node/function."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Get parameters
            event_types = kwargs.get('event_types', [])
            min_confidence = kwargs.get('min_confidence', 0.0)
            since_date = kwargs.get('since_date')
            
            # Build query to find events related to this node/function
            query = """
                SELECT * FROM semantic_events 
                WHERE project_id = ?
                AND (location LIKE ? OR details LIKE ? OR node_id LIKE ?)
                AND confidence >= ?
            """
            params = [project_id, f"%{node_id}%", f"%{node_id}%", f"%{node_id}%", min_confidence]
            
            if event_types:
                placeholders = ','.join(['?' for _ in event_types])
                query += f" AND event_type IN ({placeholders})"
                params.extend(event_types)
            
            if since_date:
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND created_at > ?"
                params.append(timestamp)
            
            query += " ORDER BY created_at ASC"
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return f"📜 Evolution History: No events found for '{node_id}'"
            
            result = f"📜 Evolution History for '{node_id}' ({len(events)} events):\n\n"
            for i, event in enumerate(events, 1):
                result += f"{i}. **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"   - Location: `{event[5]}`\n"     # location
                result += f"   - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"   - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                if event[6]:  # details
                    result += f"   - Details: {event[6]}\n"
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting filtered evolution: {str(e)}"
    
    def debug_query_tools(self, project_path: str) -> str:
        """Diagnostic information for debugging query issues."""
        try:
            # Get project ID and info
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Debug: Project not registered: {project_path}"
            
            project_info = self.db.get_project_info(project_id)
            project_name = project_info.get('name', 'Unknown') if project_info else 'Unknown'
            
            with self.get_connection() as conn:
                # Get basic stats
                cursor = conn.execute("SELECT COUNT(*) FROM semantic_events WHERE project_id = ?", (project_id,))
                total_events = cursor.fetchone()[0]
                
                # Get event types
                cursor = conn.execute("""
                    SELECT event_type, COUNT(*) FROM semantic_events 
                    WHERE project_id = ? GROUP BY event_type
                """, (project_id,))
                event_types = cursor.fetchall()
                
                # Get layers
                cursor = conn.execute("""
                    SELECT layer, COUNT(*) FROM semantic_events 
                    WHERE project_id = ? GROUP BY layer
                """, (project_id,))
                layers = cursor.fetchall()
            
            result = f"🔧 Debug Information for '{project_name}':\n\n"
            result += f"Project ID: {project_id}\n"
            result += f"Path: {project_path}\n"
            result += f"Total Events: {total_events}\n\n"
            
            if event_types:
                result += "Event Types:\n"
                for event_type, count in event_types:
                    result += f"  - {event_type}: {count}\n"
                result += "\n"
            
            if layers:
                result += "Layers:\n"
                for layer, count in layers:
                    result += f"  - {layer}: {count}\n"
            
            return result
        except Exception as e:
            return f"❌ Error in debug query: {str(e)}"
    
    def get_connection(self):
        """Get database connection."""
        return self.db.get_connection()


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
from svcs_core import process_commit
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
        
        # Only install post-commit hook (not pre-commit to avoid double analysis)
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
        
        # Remove SVCS hooks
        for hook_name in ["post-commit", "pre-commit"]:  # Remove both in case of old installations
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
    
    def query_semantic_events(self, project_id: Optional[str] = None, 
                             event_type: Optional[str] = None, 
                             limit: int = 10) -> List[Dict[str, Any]]:
        """Query semantic events with optional filters."""
        query = """
            SELECT 
                se.event_id,
                se.project_id,
                se.commit_hash,
                se.event_type,
                se.node_id,
                se.location,
                se.details,
                se.layer,
                se.confidence,
                se.created_at,
                c.author,
                c.timestamp,
                c.message,
                p.name as project_name
            FROM semantic_events se
            LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
            LEFT JOIN projects p ON se.project_id = p.project_id
            WHERE 1=1
        """
        
        params = []
        
        if project_id:
            query += " AND se.project_id = ?"
            params.append(project_id)
        
        if event_type:
            query += " AND se.event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY se.created_at DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                results.append(event)
        
        return results
    
    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a specific project."""
        with self.get_connection() as conn:
            # Total events
            cursor = conn.execute(
                "SELECT COUNT(*) FROM semantic_events WHERE project_id = ?",
                (project_id,)
            )
            total_events = cursor.fetchone()[0]
            
            # Event types breakdown
            cursor = conn.execute("""
                SELECT event_type, COUNT(*) as count 
                FROM semantic_events 
                WHERE project_id = ? 
                GROUP BY event_type 
                ORDER BY count DESC
            """, (project_id,))
            event_types = dict(cursor.fetchall())
            
            # Layer breakdown
            cursor = conn.execute("""
                SELECT layer, COUNT(*) as count 
                FROM semantic_events 
                WHERE project_id = ? 
                GROUP BY layer 
                ORDER BY count DESC
            """, (project_id,))
            layers = dict(cursor.fetchall())
            
            # Recent commits
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT commit_hash) 
                FROM semantic_events 
                WHERE project_id = ?
            """, (project_id,))
            total_commits = cursor.fetchone()[0]
            
            return {
                "total_events": total_events,
                "total_commits": total_commits,
                "event_types": event_types,
                "layers": layers
            }
    
    def search_events_advanced(self, project_path: str, **kwargs) -> str:
        """Advanced search with comprehensive filtering options."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Build query with filters
            query = "SELECT * FROM semantic_events WHERE project_id = ?"
            params = [project_id]
            
            # Apply filters
            if kwargs.get('event_types'):
                placeholders = ','.join(['?' for _ in kwargs['event_types']])
                query += f" AND event_type IN ({placeholders})"
                params.extend(kwargs['event_types'])
                
            if kwargs.get('since_date'):
                # Parse date - could be "YYYY-MM-DD" or "N days ago"
                since_date = kwargs['since_date']
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    # Parse YYYY-MM-DD format
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND created_at > ?"
                params.append(timestamp)
            
            if kwargs.get('location_pattern'):
                query += " AND location LIKE ?"
                params.append(f"%{kwargs['location_pattern']}%")
                
            if kwargs.get('min_confidence'):
                query += " AND confidence >= ?"
                params.append(kwargs['min_confidence'])
            
            # Order and limit
            order_by = kwargs.get('order_by', 'created_at')
            order_desc = kwargs.get('order_desc', True)
            limit = kwargs.get('limit', 20)
            
            query += f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'} LIMIT ?"
            params.append(limit)
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return "🔍 Advanced Search Results: No events found matching the criteria"
            
            result = f"🔍 Advanced Search Results ({len(events)} events):\n\n"
            for event in events:
                result += f"• **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"  - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                if event[6]:  # details
                    result += f"  - Details: {event[6]}\n"
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error in advanced search: {str(e)}"
    
    def get_recent_activity(self, project_path: str, **kwargs) -> str:
        """Get recent project activity with filtering options."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Get parameters
            days = kwargs.get('days', 7)
            limit = kwargs.get('limit', 15)
            layers = kwargs.get('layers', [])
            
            # Build query
            since_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
            query = "SELECT * FROM semantic_events WHERE project_id = ? AND created_at > ?"
            params = [project_id, since_timestamp]
                
            if layers:
                placeholders = ','.join(['?' for _ in layers])
                query += f" AND layer IN ({placeholders})"
                params.extend(layers)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return f"📈 Recent Activity (last {days} days): No activity found"
            
            result = f"📈 Recent Activity (last {days} days, {len(events)} events):\n\n"
            for event in events:
                result += f"• **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"  - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting recent activity: {str(e)}"
    
    def search_semantic_patterns(self, project_path: str, pattern_type: str, **kwargs) -> str:
        """Search for specific AI-detected semantic patterns."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Get parameters
            min_confidence = kwargs.get('min_confidence', 0.7)
            limit = kwargs.get('limit', 10)
            since_date = kwargs.get('since_date')
            
            # Build query to search for pattern in description or event_type
            query = """
                SELECT * FROM semantic_events 
                WHERE project_id = ? 
                AND (event_type LIKE ? OR details LIKE ?)
                AND confidence >= ?
            """
            params = [project_id, f"%{pattern_type}%", f"%{pattern_type}%", min_confidence]
            
            if since_date:
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND created_at > ?"
                params.append(timestamp)
            
            query += " ORDER BY confidence DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return f"🔍 Semantic Pattern Search: No '{pattern_type}' patterns found"
            
            result = f"🔍 Semantic Pattern Search: '{pattern_type}' ({len(events)} matches):\n\n"
            for event in events:
                result += f"• **{event[3]}** (confidence: {event[9]:.2f})\n"  # event_type, confidence
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"  - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                if event[6]:  # details
                    result += f"  - Details: {event[6]}\n"
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error searching semantic patterns: {str(e)}"
    
    def get_filtered_evolution(self, project_path: str, node_id: str, **kwargs) -> str:
        """Get filtered evolution history for a specific node/function."""
        try:
            # Get project ID
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Error: Project not registered: {project_path}"
            
            # Get parameters
            event_types = kwargs.get('event_types', [])
            min_confidence = kwargs.get('min_confidence', 0.0)
            since_date = kwargs.get('since_date')
            
            # Build query to find events related to this node/function
            query = """
                SELECT * FROM semantic_events 
                WHERE project_id = ?
                AND (location LIKE ? OR details LIKE ? OR node_id LIKE ?)
                AND confidence >= ?
            """
            params = [project_id, f"%{node_id}%", f"%{node_id}%", f"%{node_id}%", min_confidence]
            
            if event_types:
                placeholders = ','.join(['?' for _ in event_types])
                query += f" AND event_type IN ({placeholders})"
                params.extend(event_types)
            
            if since_date:
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND created_at > ?"
                params.append(timestamp)
            
            query += " ORDER BY created_at ASC"
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                events = cursor.fetchall()
            
            if not events:
                return f"📜 Evolution History: No events found for '{node_id}'"
            
            result = f"📜 Evolution History for '{node_id}' ({len(events)} events):\n\n"
            for i, event in enumerate(events, 1):
                result += f"{i}. **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"   - Location: `{event[5]}`\n"     # location
                result += f"   - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"   - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                if event[6]:  # details
                    result += f"   - Details: {event[6]}\n"
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting filtered evolution: {str(e)}"
    
    def debug_query_tools(self, project_path: str) -> str:
        """Diagnostic information for debugging query issues."""
        try:
            # Get project ID and info
            project_id = self.db.get_project_id_by_path(project_path)
            if not project_id:
                return f"❌ Debug: Project not registered: {project_path}"
            
            project_info = self.db.get_project_info(project_id)
            project_name = project_info.get('name', 'Unknown') if project_info else 'Unknown'
            
            with self.get_connection() as conn:
                # Get basic stats
                cursor = conn.execute("SELECT COUNT(*) FROM semantic_events WHERE project_id = ?", (project_id,))
                total_events = cursor.fetchone()[0]
                
                # Get event types
                cursor = conn.execute("""
                    SELECT event_type, COUNT(*) FROM semantic_events 
                    WHERE project_id = ? GROUP BY event_type
                """, (project_id,))
                event_types = cursor.fetchall()
                
                # Get layers
                cursor = conn.execute("""
                    SELECT layer, COUNT(*) FROM semantic_events 
                    WHERE project_id = ? GROUP BY layer
                """, (project_id,))
                layers = cursor.fetchall()
            
            result = f"🔧 Debug Information for '{project_name}':\n\n"
            result += f"Project ID: {project_id}\n"
            result += f"Path: {project_path}\n"
            result += f"Total Events: {total_events}\n\n"
            
            if event_types:
                result += "Event Types:\n"
                for event_type, count in event_types:
                    result += f"  - {event_type}: {count}\n"
                result += "\n"
            
            if layers:
                result += "Layers:\n"
                for layer, count in layers:
                    result += f"  - {layer}: {count}\n"
            
            return result
        except Exception as e:
            return f"❌ Error in debug query: {str(e)}"
    
    def get_connection(self):
        """Get database connection."""
        return self.db.get_connection()

def process_commit(repo_path: str):
    """Process a git commit for semantic analysis."""
    logger.info(f"Processing commit in: {repo_path}")
    
    try:
        # Import the semantic analyzer and rich for tables
        import sys
        from pathlib import Path
        from rich.console import Console
        from rich.table import Table
        from rich import box
        
        # Add paths for imports
        script_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(script_dir / ".svcs"))
        
        from svcs_complete_5layer import SVCSComplete5LayerAnalyzer
        import subprocess
        import time
        
        # Initialize components
        db = GlobalSVCSDatabase()
        analyzer = SVCSComplete5LayerAnalyzer()
        console = Console()
        
        # Normalize repo path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
        repo_path = str(Path(repo_path).resolve())
        
        # Get project info
        project = db.get_project_by_path(repo_path)
        if not project:
            print(f"⚠️  Project not registered: {repo_path}")
            logger.warning(f"Project not registered: {repo_path}")
            return
        
        project_id = project['project_id']
        project_name = project['name']
        
        # Get latest commit hash
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip()
        except subprocess.CalledProcessError:
            print("❌ Could not get commit hash")
            logger.error("Could not get commit hash")
            return
        
        # Get commit metadata
        try:
            # Get author
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%an', commit_hash],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            author = result.stdout.strip()
            
            # Get message
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%s', commit_hash],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_message = result.stdout.strip()
            
            # Get timestamp
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%ct', commit_hash],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            timestamp = int(result.stdout.strip())
            
        except subprocess.CalledProcessError:
            author = "Unknown"
            commit_message = "Unknown"
            timestamp = int(time.time())
        
        # Header matching original .svcs format
        console.print("\n[bold cyan]--=[ SVCS Semantic Analysis ]=--[/bold cyan]")
        
        # Get parent hash for debug info like original
        try:
            result = subprocess.run(
                ['git', 'rev-parse', f'{commit_hash}~1'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            parent_hash = result.stdout.strip() if result.returncode == 0 else None
        except:
            parent_hash = None
        
        console.print(f"[bold magenta][DEBUG][/bold magenta] Analyzing commit: [yellow]{commit_hash[:7]}[/yellow] (Parent: [yellow]{parent_hash[:7] if parent_hash else 'None'}[/yellow]) - Project: [cyan]{project_name}[/cyan]")
        console.print(f"[bold magenta][DEBUG][/bold magenta] Author: [blue]{author}[/blue] | Message: [white]{commit_message}[/white]")
        
        # Get changed files
        try:
            result = subprocess.run(
                ['git', 'show', '--name-only', '--format=', commit_hash],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            console.print("[bold red]❌ Could not get changed files[/bold red]")
            logger.error("Could not get changed files")
            return
        
        if not changed_files:
            console.print("[yellow]📄 No files changed in this commit[/yellow]")
            return
        
        # Store commit metadata first before storing events
        try:
            with db.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO commits (
                        project_id, commit_hash, author, message, timestamp, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    commit_hash,
                    author,
                    commit_message,
                    timestamp,
                    int(time.time())
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing commit metadata: {e}")
        
        total_events = 0
        all_file_events = []
        
        # Support multiple file types including PHP and JavaScript
        supported_extensions = ['.py', '.php', '.phtml', '.php3', '.php4', '.php5', '.phps', '.js', '.ts']
        
        # Analyze each changed file
        for file_path in changed_files:
            if not any(file_path.endswith(ext) for ext in supported_extensions):
                console.print(f"[dim]⏭️  Skipping {file_path} (unsupported file type)[/dim]")
                continue
            
            console.print(f"[bold magenta][DEBUG][/bold magenta] Processing file: [green]{file_path}[/green]")
            
            try:
                # Get file content before and after
                try:
                    result_before = subprocess.run(
                        ['git', 'show', f'{commit_hash}~1:{file_path}'],
                        cwd=repo_path,
                        capture_output=True,
                        text=True
                    )
                    before_content = result_before.stdout if result_before.returncode == 0 else ""
                except:
                    before_content = ""
                
                # Get current content
                full_path = Path(repo_path) / file_path
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        after_content = f.read()
                else:
                    console.print(f"[yellow]⚠️  File {file_path} not found[/yellow]")
                    continue
                
                # Run semantic analysis
                events = analyzer.analyze_complete(file_path, before_content, after_content)
                
                # Process and enhance events with better details
                for event in events:
                    # Add default details if missing
                    if not event.get('details'):
                        event_type = event.get('event_type', '')
                        node_id = event.get('node_id', '')
                        
                        if event_type == 'node_added':
                            if node_id.startswith('func:'):
                                event['details'] = f"Function '{node_id[5:]}' was added to the codebase"
                            elif node_id.startswith('class:'):
                                event['details'] = f"Class '{node_id[6:]}' was added to the codebase"
                            else:
                                event['details'] = f"New code element '{node_id}' was added"
                        elif event_type == 'node_removed':
                            if node_id.startswith('func:'):
                                event['details'] = f"Function '{node_id[5:]}' was removed from the codebase"
                            elif node_id.startswith('class:'):
                                event['details'] = f"Class '{node_id[6:]}' was removed from the codebase"
                            else:
                                event['details'] = f"Code element '{node_id}' was removed"
                        elif event_type == 'node_logic_changed':
                            event['details'] = f"Implementation logic of '{node_id}' was modified"
                
                all_file_events.extend(events)
                
                # Store events in database (avoid duplicates)
                stored_count = 0
                for event in events:
                    try:
                        with db.get_connection() as conn:
                            # Create a unique event ID based on content
                            event_signature = f"{project_id}_{commit_hash}_{event.get('event_type')}_{event.get('node_id')}_{file_path}"
                            event_id = f"evt_{hash(event_signature) & 0x7FFFFFFF}"  # Positive hash
                            
                            # Check if event already exists
                            cursor = conn.execute(
                                "SELECT 1 FROM semantic_events WHERE event_id = ?",
                                (event_id,)
                            )
                            if cursor.fetchone():
                                continue  # Skip duplicate
                                
                            conn.execute("""
                                INSERT INTO semantic_events (
                                    event_id, project_id, commit_hash, event_type,
                                    node_id, location, details, layer, confidence,
                                    created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                event_id,
                                project_id,
                                commit_hash,
                                event.get('event_type', 'unknown'),
                                event.get('node_id', ''),
                                file_path,
                                str(event.get('details', '')),
                                str(event.get('layer', 'core')),
                                event.get('confidence', 1.0),
                                timestamp
                            ))
                            stored_count += 1
                            total_events += 1
                    except Exception as e:
                        console.print(f"[bold red]❌ Error storing event: {e}[/bold red]")
                        logger.error(f"Error storing event: {e}")
                
            except Exception as e:
                console.print(f"[bold red]❌ Error analyzing file {file_path}: {e}[/bold red]")
                logger.error(f"Error analyzing file {file_path}: {e}")
        
        
        # Display events in a rich table matching original .svcs format
        table = Table(
            title=f"Detected Semantic Events for Commit {commit_hash[:7]}",
            box=box.MINIMAL_DOUBLE_HEAD,
            expand=True
        )
        table.add_column("Event Type", style="cyan", no_wrap=True, width=25)
        table.add_column("Semantic Node", style="magenta", no_wrap=True, width=25)
        table.add_column("Location", style="green", no_wrap=True, width=15)
        table.add_column("Details", style="yellow")
        
        if not all_file_events:
            table.add_row("[yellow]No semantic events detected.[/yellow]", "", "", "")
        else:
            for event in all_file_events:
                event_type = event.get("event_type", "N/A")
                node_id = event.get("node_id", "N/A")
                location = event.get("location", "N/A")
                details = event.get("details", "")
                
                # Add layer and confidence info to details if available
                layer = event.get("layer", "")
                confidence = event.get("confidence", 1.0)
                if layer and layer != "core":
                    details = f"[Layer {layer}] {details}"
                if confidence != 1.0:
                    details = f"{details} (confidence: {confidence:.1%})"
                
                table.add_row(event_type, node_id, location, details)
        
        console.print(table)
        
        # Summary
        if all_file_events:
            console.print(f"\nStored [bold green]{len(all_file_events)}[/bold green] semantic events in the global database.")
        
        logger.info(f"Stored {total_events} semantic events for commit {commit_hash[:8]}")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error in semantic analysis: {e}[/bold red]")
        logger.error(f"Error in process_commit: {e}")
        # Don't fail the git operation if analysis fails


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
