#!/usr/bin/env python3
"""
SVCS CLI - Command-line interface for SVCS MCP.

Provides easy commands for managing SVCS projects:
- svcs init - Register project and install hooks
- svcs remove - Unregister project and remove hooks  
- svcs status - Show project registration status
- svcs list - List all registered projects
"""

import os
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import click

from .git_hooks import GitHookManager

# Global SVCS directory and database
SVCS_HOME = Path.home() / ".svcs"
GLOBAL_DB = SVCS_HOME / "global.db"


def get_git_hook_manager() -> GitHookManager:
    """Get a configured GitHookManager instance."""
    return GitHookManager(SVCS_HOME)


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
            
            # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
            path = str(Path(path).resolve())
            
            cursor = conn.cursor()
            
            # Check if project already exists (active or inactive)
            cursor.execute("SELECT project_id, name, status FROM projects WHERE path = ?", (path,))
            existing = cursor.fetchone()
            
            if existing:
                project_id, existing_name, status = existing
                if status == 'active':
                    return f"❌ Project already registered as '{existing_name}' at {path}"
                else:
                    # Reactivate inactive project
                    cursor.execute("""
                        UPDATE projects SET 
                        name = ?, 
                        status = 'active',
                        last_analyzed = ?
                        WHERE path = ?
                    """, (name, int(datetime.now().timestamp()), path))
                    conn.commit()
                    conn.close()
                    return f"✅ Reactivated project '{name}' (was: '{existing_name}')\nProject ID: {project_id[:8]}...\nPath: {path}"
            else:
                # Create new project
                project_id = str(uuid.uuid4())
                created_at = int(datetime.now().timestamp())
                
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
    
    def search_events_advanced(self, project_path: str, **kwargs) -> str:
        """Advanced search with comprehensive filtering options."""
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
            
            # Build query with JOIN to get author information
            query = """
                SELECT se.*, c.author 
                FROM semantic_events se
                LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
                WHERE se.project_id = ?
            """
            params = [project_id]
            
            # Apply filters
            if kwargs.get('event_types'):
                placeholders = ','.join(['?' for _ in kwargs['event_types']])
                query += f" AND se.event_type IN ({placeholders})"
                params.extend(kwargs['event_types'])
            
            if kwargs.get('author'):
                query += " AND c.author = ?"
                params.append(kwargs['author'])
                
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
                query += " AND se.created_at > ?"
                params.append(timestamp)
            
            if kwargs.get('location_pattern'):
                query += " AND se.location LIKE ?"
                params.append(f"%{kwargs['location_pattern']}%")
                
            if kwargs.get('min_confidence'):
                query += " AND se.confidence >= ?"
                params.append(kwargs['min_confidence'])
            
            # Order and limit
            order_by = kwargs.get('order_by', 'se.created_at')
            order_desc = kwargs.get('order_desc', True)
            limit = kwargs.get('limit', 20)
            
            query += f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'} LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                return "🔍 Advanced Search Results: No events found matching the criteria"
            
            result = f"🔍 Advanced Search Results ({len(events)} events):\n\n"
            for event in events:
                result += f"• **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Author: {event[13] or 'Unknown'}\n"  # author from JOIN
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
            
            # Get parameters
            days = kwargs.get('days', 7)
            limit = kwargs.get('limit', 15)
            author = kwargs.get('author')
            layers = kwargs.get('layers', [])
            
            # Build query with JOIN to get author information
            since_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
            query = """
                SELECT se.*, c.author 
                FROM semantic_events se
                LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
                WHERE se.project_id = ? AND se.created_at > ?
            """
            params = [project_id, since_timestamp]
            
            if author:
                query += " AND c.author = ?"
                params.append(author)
                
            if layers:
                placeholders = ','.join(['?' for _ in layers])
                query += f" AND se.layer IN ({placeholders})"
                params.extend(layers)
            
            query += " ORDER BY se.created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                return f"📈 Recent Activity (last {days} days): No activity found"
            
            result = f"📈 Recent Activity (last {days} days, {len(events)} events):\n\n"
            for event in events:
                result += f"• **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Author: {event[13] or 'Unknown'}\n"  # author from JOIN
                result += f"  - Commit: {event[2][:8]}...\n"  # commit_hash
                result += f"  - Date: {datetime.fromtimestamp(event[12]).strftime('%Y-%m-%d %H:%M:%S')}\n"  # created_at
                result += "\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting recent activity: {str(e)}"
    
    def search_semantic_patterns(self, project_path: str, pattern_type: str, **kwargs) -> str:
        """Search for specific AI-detected semantic patterns."""
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
            
            # Get parameters
            min_confidence = kwargs.get('min_confidence', 0.7)
            limit = kwargs.get('limit', 10)
            since_date = kwargs.get('since_date')
            
            # Build query with JOIN to get author information
            query = """
                SELECT se.*, c.author 
                FROM semantic_events se
                LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
                WHERE se.project_id = ? 
                AND (se.event_type LIKE ? OR se.details LIKE ?)
                AND se.confidence >= ?
            """
            params = [project_id, f"%{pattern_type}%", f"%{pattern_type}%", min_confidence]
            
            if since_date:
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND se.created_at > ?"
                params.append(timestamp)
            
            query += " ORDER BY se.confidence DESC, se.created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                return f"🔍 Semantic Pattern Search: No '{pattern_type}' patterns found"
            
            result = f"🔍 Semantic Pattern Search: '{pattern_type}' ({len(events)} matches):\n\n"
            for event in events:
                result += f"• **{event[3]}** (confidence: {event[9]:.2f})\n"  # event_type, confidence
                result += f"  - Location: `{event[5]}`\n"     # location
                result += f"  - Author: {event[13] or 'Unknown'}\n"  # author from JOIN
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
            
            # Get parameters
            event_types = kwargs.get('event_types', [])
            min_confidence = kwargs.get('min_confidence', 0.0)
            since_date = kwargs.get('since_date')
            
            # Build query with JOIN to get author information
            query = """
                SELECT se.*, c.author 
                FROM semantic_events se
                LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
                WHERE se.project_id = ?
                AND (se.location LIKE ? OR se.details LIKE ? OR se.node_id LIKE ?)
                AND se.confidence >= ?
            """
            params = [project_id, f"%{node_id}%", f"%{node_id}%", f"%{node_id}%", min_confidence]
            
            if event_types:
                placeholders = ','.join(['?' for _ in event_types])
                query += f" AND se.event_type IN ({placeholders})"
                params.extend(event_types)
            
            if since_date:
                if 'days ago' in since_date:
                    days = int(since_date.split()[0])
                    timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                else:
                    date_obj = datetime.strptime(since_date, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                query += " AND se.created_at > ?"
                params.append(timestamp)
            
            query += " ORDER BY se.created_at ASC"
            
            cursor.execute(query, params)
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                return f"📜 Evolution History: No events found for '{node_id}'"
            
            result = f"📜 Evolution History for '{node_id}' ({len(events)} events):\n\n"
            for i, event in enumerate(events, 1):
                result += f"{i}. **{event[3]}** ({event[7]})\n"  # event_type, layer
                result += f"   - Location: `{event[5]}`\n"     # location
                result += f"   - Author: {event[13] or 'Unknown'}\n"  # author from JOIN
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
            conn = self.get_connection()
            if not conn:
                return "❌ Error: SVCS database not found"
            
            # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
            project_path = str(Path(project_path).resolve())
            
            cursor = conn.cursor()
            
            # Check project registration
            cursor.execute("SELECT project_id, name FROM projects WHERE path = ? AND status = 'active'", (project_path,))
            project_row = cursor.fetchone()
            if not project_row:
                return f"❌ Debug: Project not registered: {project_path}"
            
            project_id, project_name = project_row
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM semantic_events WHERE project_id = ?", (project_id,))
            total_events = cursor.fetchone()[0]
            
            # Get event types
            cursor.execute("""
                SELECT event_type, COUNT(*) FROM semantic_events 
                WHERE project_id = ? GROUP BY event_type
            """, (project_id,))
            event_types = cursor.fetchall()
            
            # Get layers
            cursor.execute("""
                SELECT layer, COUNT(*) FROM semantic_events 
                WHERE project_id = ? GROUP BY layer
            """, (project_id,))
            layers = cursor.fetchall()
            
            # Get authors from commits
            cursor.execute("""
                SELECT c.author, COUNT(se.event_id) 
                FROM commits c
                LEFT JOIN semantic_events se ON c.commit_hash = se.commit_hash AND c.project_id = se.project_id
                WHERE c.project_id = ? AND c.author IS NOT NULL
                GROUP BY c.author
            """, (project_id,))
            authors = cursor.fetchall()
            
            conn.close()
            
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
                result += "\n"
            
            if authors:
                result += "Authors:\n"
                for author, count in authors:
                    result += f"  - {author}: {count} events\n"
            
            return result
        except Exception as e:
            return f"❌ Error in debug query: {str(e)}"

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

    def prune_orphaned_data(self, project_path: str = None) -> str:
        """Remove semantic data for commits no longer in Git history."""
        try:
            import subprocess
            import sqlite3
            
            conn = self.get_connection()
            if not conn:
                return "❌ No SVCS database found. Please run 'svcs init' first."
            
            cursor = conn.cursor()
            
            if project_path:
                # Normalize path to resolve symlinks
                project_path = str(Path(project_path).resolve())
                
                # Get project ID
                cursor.execute("SELECT project_id FROM projects WHERE path = ? AND status = 'active'", (project_path,))
                project_row = cursor.fetchone()
                if not project_row:
                    conn.close()
                    return f"❌ Project not registered: {project_path}"
                
                project_id = project_row[0]
                
                # Get valid commit hashes for this specific project's git repository
                try:
                    result = subprocess.run(
                        ["git", "rev-list", "--all"], 
                        cwd=project_path,
                        capture_output=True, 
                        text=True, 
                        check=True
                    )
                    git_hashes = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
                except subprocess.CalledProcessError:
                    conn.close()
                    return f"❌ Error accessing git repository at {project_path}"
                
                # Get database commit hashes for this project
                cursor.execute("SELECT DISTINCT commit_hash FROM semantic_events WHERE project_id = ?", (project_id,))
                db_hashes = {row[0] for row in cursor.fetchall()}
                
                # Find orphaned hashes
                orphaned_hashes = db_hashes - git_hashes
                
                if not orphaned_hashes:
                    conn.close()
                    return f"✅ No orphaned data found for project: {project_path}"
                
                # Remove orphaned data
                with conn:
                    for hash_val in orphaned_hashes:
                        cursor.execute("DELETE FROM semantic_events WHERE project_id = ? AND commit_hash = ?", (project_id, hash_val))
                        cursor.execute("DELETE FROM commits WHERE project_id = ? AND commit_hash = ?", (project_id, hash_val))
                
                conn.close()
                return f"✅ Successfully pruned data for {len(orphaned_hashes)} orphaned commit(s) in project: {project_path}"
            else:
                # Global prune - check all projects
                cursor.execute("SELECT project_id, path FROM projects WHERE status = 'active'")
                projects = cursor.fetchall()
                
                total_pruned = 0
                results = []
                
                for project_id, path in projects:
                    try:
                        # Get valid commit hashes for this project's git repository
                        result = subprocess.run(
                            ["git", "rev-list", "--all"], 
                            cwd=path,
                            capture_output=True, 
                            text=True, 
                            check=True
                        )
                        git_hashes = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
                        
                        # Get database commit hashes for this project
                        cursor.execute("SELECT DISTINCT commit_hash FROM semantic_events WHERE project_id = ?", (project_id,))
                        db_hashes = {row[0] for row in cursor.fetchall()}
                        
                        # Find orphaned hashes
                        orphaned_hashes = db_hashes - git_hashes
                        
                        if orphaned_hashes:
                            # Remove orphaned data
                            for hash_val in orphaned_hashes:
                                cursor.execute("DELETE FROM semantic_events WHERE project_id = ? AND commit_hash = ?", (project_id, hash_val))
                                cursor.execute("DELETE FROM commits WHERE project_id = ? AND commit_hash = ?", (project_id, hash_val))
                            
                            total_pruned += len(orphaned_hashes)
                            results.append(f"  - {path}: {len(orphaned_hashes)} orphaned commit(s)")
                    except subprocess.CalledProcessError:
                        results.append(f"  - {path}: ⚠️  Git repository not accessible")
                
                conn.commit()
                conn.close()
                
                if total_pruned > 0:
                    result_text = f"✅ Successfully pruned data for {total_pruned} orphaned commit(s) across {len(projects)} project(s):\n"
                    result_text += "\n".join(results)
                    return result_text
                else:
                    return "✅ No orphaned data found across all registered projects."
                    
        except Exception as e:
            return f"❌ Error during prune operation: {str(e)}"
    
    def purge_project(self, path: str) -> str:
        """Permanently delete a project and all related data from the database."""
        try:
            conn = self.get_connection()
            if not conn:
                return "❌ Error: SVCS database not found"
            
            # Normalize path to resolve symlinks (e.g., /tmp -> /private/tmp on macOS)
            path = str(Path(path).resolve())
            
            cursor = conn.cursor()
            
            # Get project info before deletion
            cursor.execute("SELECT project_id, name FROM projects WHERE path = ?", (path,))
            project_row = cursor.fetchone()
            if not project_row:
                return f"❌ Error: Project not found: {path}"
            
            project_id, project_name = project_row
            
            # Count related data before deletion
            cursor.execute("SELECT COUNT(*) FROM semantic_events WHERE project_id = ?", (project_id,))
            events_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM commits WHERE project_id = ?", (project_id,))
            commits_count = cursor.fetchone()[0]
            
            # Delete all related data in the correct order (foreign keys)
            cursor.execute("DELETE FROM semantic_events WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM commits WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            
            conn.commit()
            conn.close()
            
            return f"🗑️ Successfully purged project '{project_name}'\n" \
                   f"   • Deleted {events_count} semantic events\n" \
                   f"   • Deleted {commits_count} commit records\n" \
                   f"   • Removed project registration\n" \
                   f"   • Path: {path}"
        except Exception as e:
            return f"❌ Error purging project: {str(e)}"


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
        hook_manager = get_git_hook_manager()
        
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
            'created_at': datetime.now().isoformat()
        }
        
        with open(local_svcs / 'config.yaml', 'w') as f:
            import yaml
            yaml.dump(config, f)
        
        click.echo(f"📝 Created local config: {local_svcs / 'config.yaml'}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--purge', is_flag=True, help='Permanently delete all project data from database (cannot be undone)')
def remove(path: str, purge: bool):
    """Remove SVCS from a project (unregister and remove hooks).
    
    By default, this performs a 'soft delete' - the project is marked as inactive
    but all data is preserved and can be recovered by re-registering.
    
    Use --purge to permanently delete ALL project data including semantic events
    and commit history. This action cannot be undone!
    """
    path = os.path.abspath(path)
    
    try:
        if purge:
            # Confirm destructive action
            click.echo(f"⚠️  WARNING: This will permanently delete ALL data for project at {path}")
            click.echo("   • All semantic events will be deleted")
            click.echo("   • All commit history will be deleted") 
            click.echo("   • Project registration will be removed")
            click.echo("   • This action CANNOT be undone!")
            
            if not click.confirm("Are you absolutely sure you want to purge this project?"):
                click.echo("❌ Operation cancelled")
                return
            
            # Perform hard delete (purge)
            result = db.purge_project(path)
            click.echo(result)
        else:
            # Perform soft delete (unregister)
            result = db.unregister_project(path)
            click.echo(result)
        
        # Remove local .svcs directory if it exists
        local_svcs = Path(path) / '.svcs'
        if local_svcs.exists():
            import shutil
            shutil.rmtree(local_svcs)
            click.echo(f"🗑️ Removed local config: {local_svcs}")
        
        # Uninstall git hooks
        hook_manager = get_git_hook_manager()
        click.echo("🔗 Removing git hooks...")
        if hook_manager.uninstall_project_hooks(path):
            click.echo("✅ Git hooks removed successfully")
        else:
            click.echo("⚠️ Warning: Some git hooks failed to remove", err=True)
        
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
    hook_manager = get_git_hook_manager()
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
        global_hook_status = "✅ installed" if hook_manager.global_hook_script.exists() else "❌ not installed"
        click.echo(f"\n🌐 Global Hook: {global_hook_status}")
    
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
@click.option('--project', default='.', type=click.Path(exists=True), help='Project path')
@click.option('--event-types', multiple=True, help='Filter by event types (use multiple times for multiple types)')
@click.option('--author', help='Filter by author')
@click.option('--since', help='Filter since date (YYYY-MM-DD or "N days ago")')
@click.option('--location', help='Filter by location pattern')
@click.option('--min-confidence', type=float, help='Minimum confidence threshold')
@click.option('--limit', type=int, default=20, help='Maximum results')
@click.option('--order-by', default='created_at', help='Order by field')
@click.option('--desc/--asc', default=True, help='Sort order')
def search(project, event_types, author, since, location, min_confidence, limit, order_by, desc):
    """Advanced search for semantic events with filtering options."""
    project_path = os.path.abspath(project)
    
    try:
        kwargs = {
            'event_types': event_types if event_types else None,
            'author': author,
            'since_date': since,
            'location_pattern': location,
            'min_confidence': min_confidence,
            'limit': limit,
            'order_by': order_by,
            'order_desc': desc
        }
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        result = db.search_events_advanced(project_path, **kwargs)
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--project', default='.', type=click.Path(exists=True), help='Project path')
@click.option('--days', type=int, default=7, help='Number of days back')
@click.option('--author', help='Filter by author')
@click.option('--layers', multiple=True, help='Filter by layers')
@click.option('--limit', type=int, default=15, help='Maximum results')
def recent(project, days, author, layers, limit):
    """Get recent project activity with filtering options."""
    project_path = os.path.abspath(project)
    
    try:
        kwargs = {
            'days': days,
            'author': author,
            'layers': list(layers) if layers else None,
            'limit': limit
        }
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        result = db.get_recent_activity(project_path, **kwargs)
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('pattern_type')
@click.option('--project', default='.', type=click.Path(exists=True), help='Project path')
@click.option('--min-confidence', type=float, default=0.7, help='Minimum confidence threshold')
@click.option('--since', help='Filter since date (YYYY-MM-DD or "N days ago")')
@click.option('--limit', type=int, default=10, help='Maximum results')
def patterns(pattern_type: str, project, min_confidence, since, limit):
    """Search for specific AI-detected semantic patterns.
    
    PATTERN_TYPE: Type of pattern to search for (e.g., 'performance', 'architecture')
    """
    project_path = os.path.abspath(project)
    
    try:
        kwargs = {
            'min_confidence': min_confidence,
            'since_date': since,
            'limit': limit
        }
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        result = db.search_semantic_patterns(project_path, pattern_type, **kwargs)
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('node_id')
@click.option('--project', default='.', type=click.Path(exists=True), help='Project path')
@click.option('--event-types', multiple=True, help='Filter by event types (use multiple times for multiple types)')
@click.option('--min-confidence', type=float, default=0.0, help='Minimum confidence threshold')
@click.option('--since', help='Filter since date (YYYY-MM-DD or "N days ago")')
def evolution(node_id: str, project, event_types, min_confidence, since):
    """Get filtered evolution history for a specific node/function.
    
    NODE_ID: Identifier for the node/function (e.g., 'func:function_name')
    """
    project_path = os.path.abspath(project)
    
    try:
        kwargs = {
            'event_types': event_types if event_types else None,
            'min_confidence': min_confidence,
            'since_date': since
        }
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        result = db.get_filtered_evolution(project_path, node_id, **kwargs)
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--project', default='.', type=click.Path(exists=True), help='Project path')
def debug(project):
    """Diagnostic information for debugging query issues."""
    project_path = os.path.abspath(project)
    
    try:
        result = db.debug_query_tools(project_path)
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command() 
@click.argument('project_path', default='.', type=click.Path(exists=True))
def stats(project_path: str):
    """Show semantic evolution statistics for a project."""
    project_path = os.path.abspath(project_path)
    
    try:
        result = call_mcp_tool('get_project_statistics', {
            'path': project_path
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
        # Direct GenAI integration for natural language queries
        try:
            import google.generativeai as genai
            import os
            
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return "❌ Error: GOOGLE_API_KEY environment variable not set.\nPlease get a key from https://aistudio.google.com/app/apikey and run 'export GOOGLE_API_KEY=...'"
            
            genai.configure(api_key=api_key)
            
            # Get project info
            project_path = args['project_path']
            query = args['query']
            
            # Create a simple AI query system
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            
            # Get recent activity as context
            recent_events = db.get_recent_activity(project_path, days=7, limit=10)
            
            prompt = f"""You are an SVCS semantic analysis assistant. A developer is asking about their codebase evolution.

Project path: {project_path}
Developer query: {query}

Recent activity (last 7 days):
{recent_events}

Based on the recent activity, provide a helpful response about the codebase evolution. If the query is about specific functions or changes, refer to the activity data. If you need more specific data, suggest using the CLI commands like 'svcs search', 'svcs recent', or 'svcs patterns'."""

            response = model.generate_content(prompt)
            return f"🤖 SVCS AI Assistant:\n\n{response.text}"
            
        except ImportError:
            return "❌ Error: google-generativeai library not installed.\nPlease run: pip install google-generativeai"
        except Exception as e:
            return f"❌ Error in AI query: {str(e)}"
    else:
        return f"🚧 Tool '{tool_name}' not yet implemented"


@main.command()
@click.option('--project', help='Project path to prune (default: current directory)')
@click.option('--dry-run', is_flag=True, help='Show what would be pruned without actually doing it')
def prune(project, dry_run):
    """Remove semantic data for orphaned commits (after rebase, reset, etc.)."""
    try:
        import sys
        import os
        
        # Single project only - the API works in project context
        project_path = project or os.getcwd()
        
        if dry_run:
            click.echo(f"🔍 Dry run: Would prune orphaned data from {project_path}")
            # TODO: Implement dry-run logic for single project
            return
        
        # Check if project has SVCS database
        svcs_db_path = os.path.join(project_path, '.svcs', 'history.db')
        if not os.path.exists(svcs_db_path):
            click.echo(f"❌ No SVCS database found in {project_path}")
            click.echo("Run 'svcs init' to initialize SVCS for this project.")
            return
        
        # Add the main SVCS directory to path to access the .svcs module
        svcs_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        svcs_module_path = os.path.join(svcs_root, '.svcs')
        sys.path.insert(0, svcs_module_path)
        
        # Import the API module from .svcs directory
        import api as svcs_api
        
        # Change to project directory for prune operation
        original_cwd = os.getcwd()
        try:
            os.chdir(project_path)
            removed = svcs_api.prune_orphaned_data()
            
            if removed > 0:
                click.echo(f"🧹 Removed {removed} orphaned semantic records from {project_path}")
            else:
                click.echo(f"✨ No orphaned data found in {project_path}")
        finally:
            os.chdir(original_cwd)
                
    except Exception as e:
        click.echo(f"❌ Error during prune: {str(e)}")


@main.command()
@click.option('--show-inactive', is_flag=True, help='Show inactive (soft-deleted) projects')
@click.option('--show-stats', is_flag=True, help='Show database statistics')
def cleanup(show_inactive: bool, show_stats: bool):
    """Database cleanup utilities and inactive project management.
    
    Use this command to:
    - View inactive projects that can be purged
    - See database usage statistics
    - Identify projects that can be safely removed
    """
    try:
        if show_stats:
            # Show database statistics
            conn = db.get_connection()
            if not conn:
                click.echo("❌ Error: SVCS database not found")
                return
            
            cursor = conn.cursor()
            
            # Get project counts
            cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
            active_projects = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'inactive'")
            inactive_projects = cursor.fetchone()[0]
            
            # Get event counts
            cursor.execute("SELECT COUNT(*) FROM semantic_events")
            total_events = cursor.fetchone()[0]
            
            # Get events from inactive projects
            cursor.execute("""
                SELECT COUNT(*) FROM semantic_events se 
                JOIN projects p ON se.project_id = p.project_id 
                WHERE p.status = 'inactive'
            """)
            inactive_events = cursor.fetchone()[0]
            
            # Get commit counts
            cursor.execute("SELECT COUNT(*) FROM commits")
            total_commits = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM commits c 
                JOIN projects p ON c.project_id = p.project_id 
                WHERE p.status = 'inactive'
            """)
            inactive_commits = cursor.fetchone()[0]
            
            conn.close()
            
            click.echo("📊 SVCS Database Statistics:")
            click.echo("=" * 40)
            click.echo(f"Projects:")
            click.echo(f"  • Active: {active_projects}")
            click.echo(f"  • Inactive: {inactive_projects}")
            click.echo(f"  • Total: {active_projects + inactive_projects}")
            click.echo()
            click.echo(f"Semantic Events:")
            click.echo(f"  • From active projects: {total_events - inactive_events}")
            click.echo(f"  • From inactive projects: {inactive_events}")
            click.echo(f"  • Total: {total_events}")
            click.echo()
            click.echo(f"Commit Records:")
            click.echo(f"  • From active projects: {total_commits - inactive_commits}")
            click.echo(f"  • From inactive projects: {inactive_commits}")
            click.echo(f"  • Total: {total_commits}")
            
            if inactive_projects > 0:
                click.echo()
                click.echo(f"💡 You have {inactive_projects} inactive projects using {inactive_events} events")
                click.echo("   Use 'svcs cleanup --show-inactive' to see them")
                click.echo("   Use 'svcs remove --purge <path>' to permanently delete them")
        
        if show_inactive:
            # Show inactive projects
            conn = db.get_connection()
            if not conn:
                click.echo("❌ Error: SVCS database not found")
                return
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, p.project_id, p.path, p.created_at,
                       COUNT(se.event_id) as event_count,
                       COUNT(c.commit_hash) as commit_count
                FROM projects p
                LEFT JOIN semantic_events se ON p.project_id = se.project_id
                LEFT JOIN commits c ON p.project_id = c.project_id
                WHERE p.status = 'inactive'
                GROUP BY p.project_id, p.name, p.path, p.created_at
                ORDER BY p.created_at DESC
            """)
            inactive_projects = cursor.fetchall()
            conn.close()
            
            if not inactive_projects:
                click.echo("✨ No inactive projects found")
                return
            
            click.echo(f"🗑️ Inactive Projects ({len(inactive_projects)}):")
            click.echo("=" * 50)
            
            total_wasted_events = 0
            total_wasted_commits = 0
            
            for name, project_id, path, created_at, event_count, commit_count in inactive_projects:
                click.echo(f"• **{name}**")
                click.echo(f"  - ID: `{project_id[:8]}...`")
                click.echo(f"  - Path: `{path}`")
                click.echo(f"  - Created: {datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')}")
                click.echo(f"  - Events: {event_count}, Commits: {commit_count}")
                click.echo(f"  - Purge: `svcs remove --purge '{path}'`")
                click.echo()
                
                total_wasted_events += event_count
                total_wasted_commits += commit_count
            
            click.echo(f"📈 Total wasted storage:")
            click.echo(f"   • {total_wasted_events} semantic events")
            click.echo(f"   • {total_wasted_commits} commit records")
            click.echo()
            click.echo("💡 To permanently delete a project and free up space:")
            click.echo("   svcs remove --purge <project_path>")
        
        if not show_inactive and not show_stats:
            click.echo("Use --show-stats or --show-inactive to see cleanup information")
            click.echo("Run 'svcs cleanup --help' for more details")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
